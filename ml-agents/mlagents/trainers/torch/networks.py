from typing import Callable, List, Dict, Tuple, Optional, Union
import abc

from mlagents.torch_utils import torch, nn

from mlagents_envs.base_env import ActionSpec, ObservationSpec
from mlagents.trainers.torch.action_model import ActionModel
from mlagents.trainers.torch.agent_action import AgentAction
from mlagents.trainers.torch.action_log_probs import ActionLogProbs
from mlagents.trainers.settings import NetworkSettings
from mlagents.trainers.torch.utils import ModelUtils
from mlagents.trainers.torch.decoders import ValueHeads
from mlagents.trainers.torch.layers import LSTM, LinearEncoder, Initialization
from mlagents.trainers.torch.encoders import VectorInput
from mlagents.trainers.buffer import AgentBuffer
from mlagents.trainers.trajectory import ObsUtil
from mlagents.trainers.torch.attention import (
    EntityEmbedding,
    ResidualSelfAttention,
    get_zero_entities_mask,
)


ActivationFunction = Callable[[torch.Tensor], torch.Tensor]
EncoderFunction = Callable[
    [torch.Tensor, int, ActivationFunction, int, str, bool], torch.Tensor
]

EPSILON = 1e-7


class NetworkBody(nn.Module):
    def __init__(
        self,
        observation_specs: List[ObservationSpec],
        network_settings: NetworkSettings,
        encoded_act_size: int = 0,
    ):
        super().__init__()
        self.normalize = network_settings.normalize
        self.use_lstm = network_settings.memory is not None
        self.h_size = network_settings.hidden_units
        self.m_size = (
            network_settings.memory.memory_size
            if network_settings.memory is not None
            else 0
        )

        self.processors, self.embedding_sizes = ModelUtils.create_input_processors(
            observation_specs,
            self.h_size,
            network_settings.vis_encode_type,
            normalize=self.normalize,
        )

        entity_num_max: int = 0
        var_processors = [p for p in self.processors if isinstance(p, EntityEmbedding)]
        for processor in var_processors:
            entity_max: int = processor.entity_num_max_elements
            # Only adds entity max if it was known at construction
            if entity_max > 0:
                entity_num_max += entity_max
        if len(var_processors) > 0:
            if sum(self.embedding_sizes):
                self.x_self_encoder = LinearEncoder(
                    sum(self.embedding_sizes),
                    1,
                    self.h_size,
                    kernel_init=Initialization.Normal,
                    kernel_gain=(0.125 / self.h_size) ** 0.5,
                )
            self.rsa = ResidualSelfAttention(self.h_size, entity_num_max)
            total_enc_size = sum(self.embedding_sizes) + self.h_size
        else:
            total_enc_size = sum(self.embedding_sizes)

        total_enc_size += encoded_act_size
        self.linear_encoder = LinearEncoder(
            total_enc_size, network_settings.num_layers, self.h_size
        )

        if self.use_lstm:
            self.lstm = LSTM(self.h_size, self.m_size)
        else:
            self.lstm = None  # type: ignore

    def update_normalization(self, buffer: AgentBuffer) -> None:
        obs = ObsUtil.from_buffer(buffer, len(self.processors))
        for vec_input, enc in zip(obs, self.processors):
            if isinstance(enc, VectorInput):
                enc.update_normalization(torch.as_tensor(vec_input))

    def copy_normalization(self, other_network: "NetworkBody") -> None:
        if self.normalize:
            for n1, n2 in zip(self.processors, other_network.processors):
                if isinstance(n1, VectorInput) and isinstance(n2, VectorInput):
                    n1.copy_normalization(n2)

    @property
    def memory_size(self) -> int:
        return self.lstm.memory_size if self.use_lstm else 0

    def forward(
        self,
        inputs: List[torch.Tensor],
        actions: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        encodes = []
        var_len_processor_inputs: List[Tuple[nn.Module, torch.Tensor]] = []

        for idx, processor in enumerate(self.processors):
            if not isinstance(processor, EntityEmbedding):
                # The input can be encoded without having to process other inputs
                obs_input = inputs[idx]
                processed_obs = processor(obs_input)
                encodes.append(processed_obs)
            else:
                var_len_processor_inputs.append((processor, inputs[idx]))
        if len(encodes) != 0:
            encoded_self = torch.cat(encodes, dim=1)
            input_exist = True
        else:
            input_exist = False
        if len(var_len_processor_inputs) > 0:
            # Some inputs need to be processed with a variable length encoder
            masks = get_zero_entities_mask([p_i[1] for p_i in var_len_processor_inputs])
            embeddings: List[torch.Tensor] = []
            processed_self = self.x_self_encoder(encoded_self) if input_exist else None
            for processor, var_len_input in var_len_processor_inputs:
                embeddings.append(processor(processed_self, var_len_input))
            qkv = torch.cat(embeddings, dim=1)
            attention_embedding = self.rsa(qkv, masks)
            if not input_exist:
                encoded_self = torch.cat([attention_embedding], dim=1)
                input_exist = True
            else:
                encoded_self = torch.cat([encoded_self, attention_embedding], dim=1)

        if not input_exist:
            raise Exception(
                "The trainer was unable to process any of the provided inputs. "
                "Make sure the trained agents has at least one sensor attached to them."
            )

        if actions is not None:
            encoded_self = torch.cat([encoded_self, actions], dim=1)
        encoding = self.linear_encoder(encoded_self)

        if self.use_lstm:
            # Resize to (batch, sequence length, encoding size)
            encoding = encoding.reshape([-1, sequence_length, self.h_size])
            encoding, memories = self.lstm(encoding, memories)
            encoding = encoding.reshape([-1, self.m_size // 2])
        return encoding, memories


class MultiInputNetworkBody(torch.nn.Module):
    def __init__(
        self,
        observation_specs: List[ObservationSpec],
        network_settings: NetworkSettings,
        action_spec: ActionSpec,
    ):
        super().__init__()
        self.normalize = network_settings.normalize
        self.use_lstm = network_settings.memory is not None
        # Scale network depending on num agents
        self.h_size = network_settings.hidden_units
        self.m_size = (
            network_settings.memory.memory_size
            if network_settings.memory is not None
            else 0
        )
        self.processors, _input_size = ModelUtils.create_input_processors(
            observation_specs,
            self.h_size,
            network_settings.vis_encode_type,
            normalize=self.normalize,
        )
        self.action_spec = action_spec

        # Modules for self-attention
        obs_only_ent_size = sum(_input_size)
        q_ent_size = (
            sum(_input_size)
            + sum(self.action_spec.discrete_branches)
            + self.action_spec.continuous_size
        )
        self.obs_encoder = EntityEmbedding(obs_only_ent_size, None, self.h_size)
        self.obs_action_encoder = EntityEmbedding(q_ent_size, None, self.h_size)

        self.self_attn = ResidualSelfAttention(self.h_size)

        self.linear_encoder = LinearEncoder(
            self.h_size,
            network_settings.num_layers,
            self.h_size,
            kernel_gain=(0.125 / self.h_size) ** 0.5,
        )

        if self.use_lstm:
            self.lstm = LSTM(self.h_size, self.m_size)
        else:
            self.lstm = None  # type: ignore

    @property
    def memory_size(self) -> int:
        return self.lstm.memory_size if self.use_lstm else 0

    def update_normalization(self, buffer: AgentBuffer) -> None:
        obs = ObsUtil.from_buffer(buffer, len(self.processors))
        for vec_input, enc in zip(obs, self.processors):
            if isinstance(enc, VectorInput):
                enc.update_normalization(torch.as_tensor(vec_input))

    def copy_normalization(self, other_network: "MultiInputNetworkBody") -> None:
        if self.normalize:
            for n1, n2 in zip(self.processors, other_network.processors):
                if isinstance(n1, VectorInput) and isinstance(n2, VectorInput):
                    n1.copy_normalization(n2)

    def _get_masks_from_nans(self, obs_tensors: List[torch.Tensor]) -> torch.Tensor:
        """
        Get attention masks by grabbing an arbitrary obs across all the agents
        Since these are raw obs, the padded values are still NaN
        """
        only_first_obs = [_all_obs[0] for _all_obs in obs_tensors]
        # Just get the first element in each obs regardless of its dimension. This will speed up
        # searching for NaNs.
        only_first_obs_flat = torch.stack(
            [_obs.flatten(start_dim=1)[:, 0] for _obs in only_first_obs], dim=1
        )
        # Get the msak from NaNs
        attn_mask = only_first_obs_flat.isnan().type(torch.FloatTensor)
        return attn_mask

    def forward(
        self,
        obs_only: List[List[torch.Tensor]],
        obs: List[List[torch.Tensor]],
        actions: List[AgentAction],
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[torch.Tensor, torch.Tensor]:

        self_attn_masks = []
        self_attn_inputs = []
        concat_f_inp = []
        obs_attn_mask = self._get_masks_from_nans(obs)
        for inputs, action in zip(obs, actions):
            encodes = []
            for idx, processor in enumerate(self.processors):
                obs_input = inputs[idx]
                obs_input[
                    obs_attn_mask.type(torch.BoolTensor)[:, idx], ::
                ] = 0.0  # Remoove NaNs fast
                processed_obs = processor(obs_input)
                encodes.append(processed_obs)
            cat_encodes = [
                torch.cat(encodes, dim=-1),
                action.to_flat(self.action_spec.discrete_branches),
            ]
            concat_f_inp.append(torch.cat(cat_encodes, dim=1))

        if concat_f_inp:
            f_inp = torch.stack(concat_f_inp, dim=1)
            self_attn_masks.append(obs_attn_mask)
            self_attn_inputs.append(self.obs_action_encoder(None, f_inp))

        concat_encoded_obs = []
        obs_only_attn_mask = self._get_masks_from_nans(obs_only)
        for inputs in obs_only:
            encodes = []
            for idx, processor in enumerate(self.processors):
                obs_input = inputs[idx]
                obs_input[
                    obs_only_attn_mask.type(torch.BoolTensor)[:, idx], ::
                ] = 0.0  # Remoove NaNs fast
                processed_obs = processor(obs_input)
                encodes.append(processed_obs)
            concat_encoded_obs.append(torch.cat(encodes, dim=-1))
        g_inp = torch.stack(concat_encoded_obs, dim=1)
        self_attn_masks.append(obs_only_attn_mask)
        self_attn_inputs.append(self.obs_encoder(None, g_inp))

        encoded_entity = torch.cat(self_attn_inputs, dim=1)
        encoded_state = self.self_attn(encoded_entity, self_attn_masks)

        encoding = self.linear_encoder(encoded_state)
        if self.use_lstm:
            # Resize to (batch, sequence length, encoding size)
            encoding = encoding.reshape([-1, sequence_length, self.h_size])
            encoding, memories = self.lstm(encoding, memories)
            encoding = encoding.reshape([-1, self.m_size // 2])
        return encoding, memories


class Critic(abc.ABC):
    @abc.abstractmethod
    def update_normalization(self, buffer: AgentBuffer) -> None:
        """
        Updates normalization of Actor based on the provided List of vector obs.
        :param vector_obs: A List of vector obs as tensors.
        """
        pass

    def critic_pass(
        self,
        inputs: List[torch.Tensor],
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[Dict[str, torch.Tensor], torch.Tensor]:
        """
        Get value outputs for the given obs.
        :param inputs: List of inputs as tensors.
        :param memories: Tensor of memories, if using memory. Otherwise, None.
        :returns: Dict of reward stream to output tensor for values.
        """
        pass


class ValueNetwork(nn.Module, Critic):
    def __init__(
        self,
        stream_names: List[str],
        observation_specs: List[ObservationSpec],
        network_settings: NetworkSettings,
        encoded_act_size: int = 0,
        outputs_per_stream: int = 1,
    ):

        # This is not a typo, we want to call __init__ of nn.Module
        nn.Module.__init__(self)
        self.network_body = NetworkBody(
            observation_specs, network_settings, encoded_act_size=encoded_act_size
        )
        if network_settings.memory is not None:
            encoding_size = network_settings.memory.memory_size // 2
        else:
            encoding_size = network_settings.hidden_units
        self.value_heads = ValueHeads(stream_names, encoding_size, outputs_per_stream)

    def update_normalization(self, buffer: AgentBuffer) -> None:
        self.network_body.update_normalization(buffer)

    @property
    def memory_size(self) -> int:
        return self.network_body.memory_size

    def critic_pass(
        self,
        inputs: List[torch.Tensor],
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[Dict[str, torch.Tensor], torch.Tensor]:
        value_outputs, critic_mem_out = self.forward(
            inputs, memories=memories, sequence_length=sequence_length
        )
        return value_outputs, critic_mem_out

    def forward(
        self,
        inputs: List[torch.Tensor],
        actions: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[Dict[str, torch.Tensor], torch.Tensor]:
        encoding, memories = self.network_body(
            inputs, actions, memories, sequence_length
        )
        output = self.value_heads(encoding)
        return output, memories


class Actor(abc.ABC):
    @abc.abstractmethod
    def update_normalization(self, buffer: AgentBuffer) -> None:
        """
        Updates normalization of Actor based on the provided List of vector obs.
        :param vector_obs: A List of vector obs as tensors.
        """
        pass

    def get_action_and_stats(
        self,
        inputs: List[torch.Tensor],
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[AgentAction, ActionLogProbs, torch.Tensor, torch.Tensor]:
        """
        Returns sampled actions.
        If memory is enabled, return the memories as well.
        :param inputs: A List of inputs as tensors.
        :param masks: If using discrete actions, a Tensor of action masks.
        :param memories: If using memory, a Tensor of initial memories.
        :param sequence_length: If using memory, the sequence length.
        :return: A Tuple of AgentAction, ActionLogProbs, entropies, and memories.
            Memories will be None if not using memory.
        """
        pass

    def get_stats(
        self,
        inputs: List[torch.Tensor],
        actions: AgentAction,
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[ActionLogProbs, torch.Tensor]:
        """
        Returns log_probs for actions and entropies.
        If memory is enabled, return the memories as well.
        :param inputs: A List of inputs as tensors.
        :param actions: AgentAction of actions.
        :param masks: If using discrete actions, a Tensor of action masks.
        :param memories: If using memory, a Tensor of initial memories.
        :param sequence_length: If using memory, the sequence length.
        :return: A Tuple of AgentAction, ActionLogProbs, entropies, and memories.
            Memories will be None if not using memory.
        """

        pass

    @abc.abstractmethod
    def forward(
        self,
        vec_inputs: List[torch.Tensor],
        vis_inputs: List[torch.Tensor],
        var_len_inputs: List[torch.Tensor],
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
    ) -> Tuple[Union[int, torch.Tensor], ...]:
        """
        Forward pass of the Actor for inference. This is required for export to ONNX, and
        the inputs and outputs of this method should not be changed without a respective change
        in the ONNX export code.
        """
        pass


class SimpleActor(nn.Module, Actor):
    def __init__(
        self,
        observation_specs: List[ObservationSpec],
        network_settings: NetworkSettings,
        action_spec: ActionSpec,
        conditional_sigma: bool = False,
        tanh_squash: bool = False,
    ):
        super().__init__()
        self.action_spec = action_spec
        self.version_number = torch.nn.Parameter(
            torch.Tensor([2.0]), requires_grad=False
        )
        self.is_continuous_int_deprecated = torch.nn.Parameter(
            torch.Tensor([int(self.action_spec.is_continuous())]), requires_grad=False
        )
        self.continuous_act_size_vector = torch.nn.Parameter(
            torch.Tensor([int(self.action_spec.continuous_size)]), requires_grad=False
        )
        # TODO: export list of branch sizes instead of sum
        self.discrete_act_size_vector = torch.nn.Parameter(
            torch.Tensor([sum(self.action_spec.discrete_branches)]), requires_grad=False
        )
        self.act_size_vector_deprecated = torch.nn.Parameter(
            torch.Tensor(
                [
                    self.action_spec.continuous_size
                    + sum(self.action_spec.discrete_branches)
                ]
            ),
            requires_grad=False,
        )
        self.network_body = NetworkBody(observation_specs, network_settings)
        if network_settings.memory is not None:
            self.encoding_size = network_settings.memory.memory_size // 2
        else:
            self.encoding_size = network_settings.hidden_units
        self.memory_size_vector = torch.nn.Parameter(
            torch.Tensor([int(self.network_body.memory_size)]), requires_grad=False
        )

        self.action_model = ActionModel(
            self.encoding_size,
            action_spec,
            conditional_sigma=conditional_sigma,
            tanh_squash=tanh_squash,
        )

    @property
    def memory_size(self) -> int:
        return self.network_body.memory_size

    def update_normalization(self, buffer: AgentBuffer) -> None:
        self.network_body.update_normalization(buffer)

    def get_action_and_stats(
        self,
        inputs: List[torch.Tensor],
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[AgentAction, ActionLogProbs, torch.Tensor, torch.Tensor]:

        encoding, memories = self.network_body(
            inputs, memories=memories, sequence_length=sequence_length
        )
        action, log_probs, entropies = self.action_model(encoding, masks)
        return action, log_probs, entropies, memories

    def get_stats(
        self,
        inputs: List[torch.Tensor],
        actions: AgentAction,
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[ActionLogProbs, torch.Tensor]:
        encoding, actor_mem_outs = self.network_body(
            inputs, memories=memories, sequence_length=sequence_length
        )
        log_probs, entropies = self.action_model.evaluate(encoding, masks, actions)

        return log_probs, entropies

    def forward(
        self,
        vec_inputs: List[torch.Tensor],
        vis_inputs: List[torch.Tensor],
        var_len_inputs: List[torch.Tensor],
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
    ) -> Tuple[Union[int, torch.Tensor], ...]:
        """
        Note: This forward() method is required for exporting to ONNX. Don't modify the inputs and outputs.

        At this moment, torch.onnx.export() doesn't accept None as tensor to be exported,
        so the size of return tuple varies with action spec.
        """
        # This code will convert the vec and vis obs into a list of inputs for the network
        concatenated_vec_obs = vec_inputs[0]
        inputs = []
        start = 0
        end = 0
        vis_index = 0
        var_len_index = 0
        for i, enc in enumerate(self.network_body.processors):
            if isinstance(enc, VectorInput):
                # This is a vec_obs
                vec_size = self.network_body.embedding_sizes[i]
                end = start + vec_size
                inputs.append(concatenated_vec_obs[:, start:end])
                start = end
            elif isinstance(enc, EntityEmbedding):
                inputs.append(var_len_inputs[var_len_index])
                var_len_index += 1
            else:  # visual input
                inputs.append(vis_inputs[vis_index])
                vis_index += 1

        # End of code to convert the vec and vis obs into a list of inputs for the network
        encoding, memories_out = self.network_body(
            inputs, memories=memories, sequence_length=1
        )

        (
            cont_action_out,
            disc_action_out,
            action_out_deprecated,
        ) = self.action_model.get_action_out(encoding, masks)
        export_out = [self.version_number, self.memory_size_vector]
        if self.action_spec.continuous_size > 0:
            export_out += [cont_action_out, self.continuous_act_size_vector]
        if self.action_spec.discrete_size > 0:
            export_out += [disc_action_out, self.discrete_act_size_vector]
        # Only export deprecated nodes with non-hybrid action spec
        if self.action_spec.continuous_size == 0 or self.action_spec.discrete_size == 0:
            export_out += [
                action_out_deprecated,
                self.is_continuous_int_deprecated,
                self.act_size_vector_deprecated,
            ]
        return tuple(export_out)


class SharedActorCritic(SimpleActor, Critic):
    def __init__(
        self,
        observation_specs: List[ObservationSpec],
        network_settings: NetworkSettings,
        action_spec: ActionSpec,
        stream_names: List[str],
        conditional_sigma: bool = False,
        tanh_squash: bool = False,
    ):
        self.use_lstm = network_settings.memory is not None
        super().__init__(
            observation_specs,
            network_settings,
            action_spec,
            conditional_sigma,
            tanh_squash,
        )
        self.stream_names = stream_names
        self.value_heads = ValueHeads(stream_names, self.encoding_size)

    def critic_pass(
        self,
        inputs: List[torch.Tensor],
        memories: Optional[torch.Tensor] = None,
        sequence_length: int = 1,
    ) -> Tuple[Dict[str, torch.Tensor], torch.Tensor]:
        encoding, memories_out = self.network_body(
            inputs, memories=memories, sequence_length=sequence_length
        )
        return self.value_heads(encoding), memories_out


class GlobalSteps(nn.Module):
    def __init__(self):
        super().__init__()
        self.__global_step = nn.Parameter(
            torch.Tensor([0]).to(torch.int64), requires_grad=False
        )

    @property
    def current_step(self):
        return int(self.__global_step.item())

    @current_step.setter
    def current_step(self, value):
        self.__global_step[:] = value

    def increment(self, value):
        self.__global_step += value


class LearningRate(nn.Module):
    def __init__(self, lr):
        # Todo: add learning rate decay
        super().__init__()
        self.learning_rate = torch.Tensor([lr])
