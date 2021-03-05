from typing import Dict, cast, List, Tuple, Optional
import numpy as np
import math
from mlagents.torch_utils import torch

from mlagents.trainers.buffer import (
    AgentBuffer,
    BufferKey,
    RewardSignalUtil,
    AgentBufferField,
)

from mlagents_envs.timers import timed
from mlagents_envs.base_env import ObservationSpec, ActionSpec
from mlagents.trainers.policy.torch_policy import TorchPolicy
from mlagents.trainers.optimizer.torch_optimizer import TorchOptimizer
from mlagents.trainers.settings import (
    ExtrinsicSettings,
    RewardSignalSettings,
    RewardSignalType,
    TrainerSettings,
    PPOSettings,
)
from mlagents.trainers.torch.networks import Critic, MultiInputNetworkBody
from mlagents.trainers.torch.decoders import ValueHeads
from mlagents.trainers.torch.agent_action import AgentAction
from mlagents.trainers.torch.action_log_probs import ActionLogProbs
from mlagents.trainers.torch.utils import ModelUtils
from mlagents.trainers.trajectory import ObsUtil, GroupObsUtil
from mlagents.trainers.settings import NetworkSettings

from mlagents_envs.logging_util import get_logger

logger = get_logger(__name__)


class TorchCOMAOptimizer(TorchOptimizer):
    class COMAValueNetwork(torch.nn.Module, Critic):
        def __init__(
            self,
            stream_names: List[str],
            observation_specs: List[ObservationSpec],
            network_settings: NetworkSettings,
            action_spec: ActionSpec,
        ):
            torch.nn.Module.__init__(self)
            self.network_body = MultiInputNetworkBody(
                observation_specs, network_settings, action_spec
            )
            if network_settings.memory is not None:
                encoding_size = network_settings.memory.memory_size // 2
            else:
                encoding_size = network_settings.hidden_units

            self.value_heads = ValueHeads(stream_names, encoding_size, 1)

        @property
        def memory_size(self) -> int:
            return self.network_body.memory_size

        def update_normalization(self, buffer: AgentBuffer) -> None:
            self.network_body.update_normalization(buffer)

        def baseline(
            self,
            self_obs: List[List[torch.Tensor]],
            obs: List[List[torch.Tensor]],
            actions: List[AgentAction],
            memories: Optional[torch.Tensor] = None,
            sequence_length: int = 1,
        ) -> Tuple[torch.Tensor, torch.Tensor]:

            encoding, memories = self.network_body(
                obs_only=self_obs,
                obs=obs,
                actions=actions,
                memories=memories,
                sequence_length=sequence_length,
            )
            value_outputs, critic_mem_out = self.forward(
                encoding, memories, sequence_length
            )
            return value_outputs, critic_mem_out

        def critic_pass(
            self,
            obs: List[List[torch.Tensor]],
            memories: Optional[torch.Tensor] = None,
            sequence_length: int = 1,
        ) -> Tuple[torch.Tensor, torch.Tensor]:

            encoding, memories = self.network_body(
                obs_only=obs,
                obs=[],
                actions=[],
                memories=memories,
                sequence_length=sequence_length,
            )
            value_outputs, critic_mem_out = self.forward(
                encoding, memories, sequence_length
            )
            return value_outputs, critic_mem_out

        def forward(
            self,
            encoding: torch.Tensor,
            memories: Optional[torch.Tensor] = None,
            sequence_length: int = 1,
        ) -> Tuple[torch.Tensor, torch.Tensor]:

            output = self.value_heads(encoding)
            return output, memories

    def __init__(self, policy: TorchPolicy, trainer_settings: TrainerSettings):
        """
        Takes a Policy and a Dict of trainer parameters and creates an Optimizer around the policy.
        The PPO optimizer has a value estimator and a loss function.
        :param policy: A TorchPolicy object that will be updated by this PPO Optimizer.
        :param trainer_params: Trainer parameters dictionary that specifies the
        properties of the trainer.
        """
        # Create the graph here to give more granular control of the TF graph to the Optimizer.

        super().__init__(policy, trainer_settings)
        reward_signal_configs = trainer_settings.reward_signals
        reward_signal_names = [key.value for key, _ in reward_signal_configs.items()]

        self._critic = TorchCOMAOptimizer.COMAValueNetwork(
            reward_signal_names,
            policy.behavior_spec.observation_specs,
            network_settings=trainer_settings.network_settings,
            action_spec=policy.behavior_spec.action_spec,
        )

        params = list(self.policy.actor.parameters()) + list(self.critic.parameters())
        self.hyperparameters: PPOSettings = cast(
            PPOSettings, trainer_settings.hyperparameters
        )
        self.decay_learning_rate = ModelUtils.DecayedValue(
            self.hyperparameters.learning_rate_schedule,
            self.hyperparameters.learning_rate,
            1e-10,
            self.trainer_settings.max_steps,
        )
        self.decay_epsilon = ModelUtils.DecayedValue(
            self.hyperparameters.learning_rate_schedule,
            self.hyperparameters.epsilon,
            0.1,
            self.trainer_settings.max_steps,
        )
        self.decay_beta = ModelUtils.DecayedValue(
            self.hyperparameters.learning_rate_schedule,
            self.hyperparameters.beta,
            1e-5,
            self.trainer_settings.max_steps,
        )

        self.optimizer = torch.optim.Adam(
            params, lr=self.trainer_settings.hyperparameters.learning_rate
        )
        self.stats_name_to_update_name = {
            "Losses/Value Loss": "value_loss",
            "Losses/Policy Loss": "policy_loss",
        }

        self.stream_names = list(self.reward_signals.keys())
        self.value_memory_dict: Dict[str, torch.Tensor] = {}
        self.baseline_memory_dict: Dict[str, torch.Tensor] = {}

    def create_reward_signals(
        self, reward_signal_configs: Dict[RewardSignalType, RewardSignalSettings]
    ) -> None:
        """
        Create reward signals. Override default to provide warnings for Curiosity and
        GAIL, and make sure Extrinsic adds team rewards.
        :param reward_signal_configs: Reward signal config.
        """
        for reward_signal, settings in reward_signal_configs.items():
            if reward_signal != RewardSignalType.EXTRINSIC:
                logger.warning(
                    f"Reward Signal {reward_signal.value} is not supported with the COMA2 trainer; \
                    results may be unexpected."
                )
            elif isinstance(settings, ExtrinsicSettings):
                settings.add_groupmate_rewards = True
        super().create_reward_signals(reward_signal_configs)

    @property
    def critic(self):
        return self._critic

    def coma_value_loss(
        self,
        values: Dict[str, torch.Tensor],
        old_values: Dict[str, torch.Tensor],
        returns: Dict[str, torch.Tensor],
        epsilon: float,
        loss_masks: torch.Tensor,
    ) -> torch.Tensor:
        """
        Evaluates value loss for PPO.
        :param values: Value output of the current network.
        :param old_values: Value stored with experiences in buffer.
        :param returns: Computed returns.
        :param epsilon: Clipping value for value estimate.
        :param loss_mask: Mask for losses. Used with LSTM to ignore 0'ed out experiences.
        """
        value_losses = []
        for name, head in values.items():
            old_val_tensor = old_values[name]
            returns_tensor = returns[name]
            clipped_value_estimate = old_val_tensor + torch.clamp(
                head - old_val_tensor, -1 * epsilon, epsilon
            )
            v_opt_a = (returns_tensor - head) ** 2
            v_opt_b = (returns_tensor - clipped_value_estimate) ** 2
            value_loss = ModelUtils.masked_mean(torch.max(v_opt_a, v_opt_b), loss_masks)
            value_losses.append(value_loss)
        value_loss = torch.mean(torch.stack(value_losses))
        return value_loss

    def ppo_policy_loss(
        self,
        advantages: torch.Tensor,
        log_probs: torch.Tensor,
        old_log_probs: torch.Tensor,
        loss_masks: torch.Tensor,
    ) -> torch.Tensor:
        """
        Evaluate PPO policy loss.
        :param advantages: Computed advantages.
        :param log_probs: Current policy probabilities
        :param old_log_probs: Past policy probabilities
        :param loss_masks: Mask for losses. Used with LSTM to ignore 0'ed out experiences.
        """
        advantage = advantages.unsqueeze(-1)

        decay_epsilon = self.hyperparameters.epsilon
        r_theta = torch.exp(log_probs - old_log_probs)
        p_opt_a = r_theta * advantage
        p_opt_b = (
            torch.clamp(r_theta, 1.0 - decay_epsilon, 1.0 + decay_epsilon) * advantage
        )
        policy_loss = -1 * ModelUtils.masked_mean(
            torch.min(p_opt_a, p_opt_b), loss_masks
        )
        return policy_loss

    @timed
    def update(self, batch: AgentBuffer, num_sequences: int) -> Dict[str, float]:
        """
        Performs update on model.
        :param batch: Batch of experiences.
        :param num_sequences: Number of sequences to process.
        :return: Results of update.
        """
        # Get decayed parameters
        decay_lr = self.decay_learning_rate.get_value(self.policy.get_current_step())
        decay_eps = self.decay_epsilon.get_value(self.policy.get_current_step())
        decay_bet = self.decay_beta.get_value(self.policy.get_current_step())
        returns = {}
        old_values = {}
        old_baseline_values = {}
        for name in self.reward_signals:
            old_values[name] = ModelUtils.list_to_tensor(
                batch[RewardSignalUtil.value_estimates_key(name)]
            )
            returns[name] = ModelUtils.list_to_tensor(
                batch[RewardSignalUtil.returns_key(name)]
            )
            old_baseline_values[name] = ModelUtils.list_to_tensor(
                batch[RewardSignalUtil.baseline_estimates_key(name)]
            )

        n_obs = len(self.policy.behavior_spec.observation_specs)
        current_obs = ObsUtil.from_buffer(batch, n_obs)
        # Convert to tensors
        current_obs = [ModelUtils.list_to_tensor(obs) for obs in current_obs]
        group_obs = GroupObsUtil.from_buffer(batch, n_obs)
        group_obs = [
            [ModelUtils.list_to_tensor(obs) for obs in _groupmate_obs]
            for _groupmate_obs in group_obs
        ]

        act_masks = ModelUtils.list_to_tensor(batch[BufferKey.ACTION_MASK])
        actions = AgentAction.from_buffer(batch)
        group_actions = AgentAction.group_from_buffer(batch)

        memories = [
            ModelUtils.list_to_tensor(batch[BufferKey.MEMORY][i])
            for i in range(0, len(batch[BufferKey.MEMORY]), self.policy.sequence_length)
        ]
        if len(memories) > 0:
            memories = torch.stack(memories).unsqueeze(0)
        value_memories = [
            ModelUtils.list_to_tensor(batch[BufferKey.CRITIC_MEMORY][i])
            for i in range(
                0, len(batch[BufferKey.CRITIC_MEMORY]), self.policy.sequence_length
            )
        ]

        baseline_memories = [
            ModelUtils.list_to_tensor(batch[BufferKey.BASELINE_MEMORY][i])
            for i in range(
                0, len(batch[BufferKey.BASELINE_MEMORY]), self.policy.sequence_length
            )
        ]

        if len(value_memories) > 0:
            value_memories = torch.stack(value_memories).unsqueeze(0)
            baseline_memories = torch.stack(baseline_memories).unsqueeze(0)

        log_probs, entropy = self.policy.evaluate_actions(
            current_obs,
            masks=act_masks,
            actions=actions,
            memories=memories,
            seq_len=self.policy.sequence_length,
        )
        all_obs = [current_obs] + group_obs
        values, _ = self.critic.critic_pass(
            all_obs,
            memories=value_memories,
            sequence_length=self.policy.sequence_length,
        )
        baselines, _ = self.critic.baseline(
            [current_obs],
            group_obs,
            group_actions,
            memories=baseline_memories,
            sequence_length=self.policy.sequence_length,
        )
        old_log_probs = ActionLogProbs.from_buffer(batch).flatten()
        log_probs = log_probs.flatten()
        loss_masks = ModelUtils.list_to_tensor(batch[BufferKey.MASKS], dtype=torch.bool)

        baseline_loss = self.coma_value_loss(
            baselines, old_baseline_values, returns, decay_eps, loss_masks
        )
        value_loss = self.coma_value_loss(
            values, old_values, returns, decay_eps, loss_masks
        )
        policy_loss = self.ppo_policy_loss(
            ModelUtils.list_to_tensor(batch[BufferKey.ADVANTAGES]),
            log_probs,
            old_log_probs,
            loss_masks,
        )
        loss = (
            policy_loss
            + 0.5 * (value_loss + 0.5 * baseline_loss)
            - decay_bet * ModelUtils.masked_mean(entropy, loss_masks)
        )

        # Set optimizer learning rate
        ModelUtils.update_learning_rate(self.optimizer, decay_lr)
        self.optimizer.zero_grad()
        loss.backward()

        self.optimizer.step()
        update_stats = {
            # NOTE: abs() is not technically correct, but matches the behavior in TensorFlow.
            # TODO: After PyTorch is default, change to something more correct.
            "Losses/Policy Loss": torch.abs(policy_loss).item(),
            "Losses/Value Loss": value_loss.item(),
            "Losses/Baseline Loss": baseline_loss.item(),
            "Policy/Learning Rate": decay_lr,
            "Policy/Epsilon": decay_eps,
            "Policy/Beta": decay_bet,
        }

        for reward_provider in self.reward_signals.values():
            update_stats.update(reward_provider.update(batch))

        return update_stats

    def get_modules(self):
        modules = {"Optimizer": self.optimizer}
        for reward_provider in self.reward_signals.values():
            modules.update(reward_provider.get_modules())
        return modules

    def _evaluate_by_sequence_team(
        self,
        self_obs: List[torch.Tensor],
        obs: List[List[torch.Tensor]],
        actions: List[AgentAction],
        init_value_mem: torch.Tensor,
        init_baseline_mem: torch.Tensor,
    ) -> Tuple[
        Dict[str, torch.Tensor],
        Dict[str, torch.Tensor],
        AgentBufferField,
        AgentBufferField,
        torch.Tensor,
        torch.Tensor,
    ]:
        """
        Evaluate a trajectory sequence-by-sequence, assembling the result. This enables us to get the
        intermediate memories for the critic.
        :param tensor_obs: A List of tensors of shape (trajectory_len, <obs_dim>) that are the agent's
            observations for this trajectory.
        :param initial_memory: The memory that preceeds this trajectory. Of shape (1,1,<mem_size>), i.e.
            what is returned as the output of a MemoryModules.
        :return: A Tuple of the value estimates as a Dict of [name, tensor], an AgentBufferField of the initial
            memories to be used during value function update, and the final memory at the end of the trajectory.
        """
        num_experiences = self_obs[0].shape[0]
        all_next_value_mem = AgentBufferField()
        all_next_baseline_mem = AgentBufferField()
        # In the buffer, the 1st sequence are the ones that are padded. So if seq_len = 3 and
        # trajectory is of length 10, the 1st sequence is [pad,pad,obs].
        # Compute the number of elements in this padded seq.
        leftover = num_experiences % self.policy.sequence_length

        # Compute values for the potentially truncated initial sequence

        first_seq_len = leftover if leftover > 0 else self.policy.sequence_length

        self_seq_obs = []
        team_seq_obs = []
        team_seq_act = []
        seq_obs = []
        for _self_obs in self_obs:
            first_seq_obs = _self_obs[0:first_seq_len]
            seq_obs.append(first_seq_obs)
        self_seq_obs.append(seq_obs)

        for team_obs, team_action in zip(obs, actions):
            seq_obs = []
            for _obs in team_obs:
                first_seq_obs = _obs[0:first_seq_len]
                seq_obs.append(first_seq_obs)
            team_seq_obs.append(seq_obs)
            _act = team_action[0:first_seq_len]
            team_seq_act.append(_act)

        # For the first sequence, the initial memory should be the one at the
        # beginning of this trajectory.
        for _ in range(first_seq_len):
            all_next_value_mem.append(ModelUtils.to_numpy(init_value_mem.squeeze()))
            all_next_baseline_mem.append(
                ModelUtils.to_numpy(init_baseline_mem.squeeze())
            )

        all_seq_obs = self_seq_obs + team_seq_obs
        init_values, _value_mem = self.critic.critic_pass(
            all_seq_obs, init_value_mem, sequence_length=first_seq_len
        )
        all_values = {
            signal_name: [init_values[signal_name]]
            for signal_name in init_values.keys()
        }

        init_baseline, _baseline_mem = self.critic.baseline(
            self_seq_obs,
            team_seq_obs,
            team_seq_act,
            init_baseline_mem,
            sequence_length=first_seq_len,
        )
        all_baseline = {
            signal_name: [init_baseline[signal_name]]
            for signal_name in init_baseline.keys()
        }

        # Evaluate other trajectories, carrying over _mem after each
        # trajectory
        for seq_num in range(
            1, math.ceil((num_experiences) / (self.policy.sequence_length))
        ):
            for _ in range(self.policy.sequence_length):
                all_next_value_mem.append(ModelUtils.to_numpy(_value_mem.squeeze()))
                all_next_baseline_mem.append(
                    ModelUtils.to_numpy(_baseline_mem.squeeze())
                )

            start = seq_num * self.policy.sequence_length - (
                self.policy.sequence_length - leftover
            )
            end = (seq_num + 1) * self.policy.sequence_length - (
                self.policy.sequence_length - leftover
            )

            self_seq_obs = []
            team_seq_obs = []
            team_seq_act = []
            seq_obs = []
            for _self_obs in self_obs:
                seq_obs.append(_obs[start:end])
            self_seq_obs.append(seq_obs)

            for team_obs, team_action in zip(obs, actions):
                seq_obs = []
                for (_obs,) in team_obs:
                    first_seq_obs = _obs[start:end]
                    seq_obs.append(first_seq_obs)
                team_seq_obs.append(seq_obs)
                _act = team_action[start:end]
                team_seq_act.append(_act)

            all_seq_obs = self_seq_obs + team_seq_obs
            values, _value_mem = self.critic.critic_pass(
                all_seq_obs, _value_mem, sequence_length=self.policy.sequence_length
            )
            all_values = {
                signal_name: [init_values[signal_name]] for signal_name in values.keys()
            }

            baselines, _baseline_mem = self.critic.baseline(
                self_seq_obs,
                team_seq_obs,
                team_seq_act,
                _baseline_mem,
                sequence_length=first_seq_len,
            )
            all_baseline = {
                signal_name: [baselines[signal_name]]
                for signal_name in baselines.keys()
            }
        # Create one tensor per reward signal
        all_value_tensors = {
            signal_name: torch.cat(value_list, dim=0)
            for signal_name, value_list in all_values.items()
        }
        all_baseline_tensors = {
            signal_name: torch.cat(baseline_list, dim=0)
            for signal_name, baseline_list in all_baseline.items()
        }
        next_value_mem = _value_mem
        next_baseline_mem = _baseline_mem
        return (
            all_value_tensors,
            all_baseline_tensors,
            all_next_value_mem,
            all_next_baseline_mem,
            next_value_mem,
            next_baseline_mem,
        )

    def get_trajectory_and_baseline_value_estimates(
        self,
        batch: AgentBuffer,
        next_obs: List[np.ndarray],
        next_group_obs: List[List[np.ndarray]],
        done: bool,
        agent_id: str = "",
    ) -> Tuple[
        Dict[str, np.ndarray],
        Dict[str, np.ndarray],
        Dict[str, float],
        Optional[AgentBufferField],
        Optional[AgentBufferField],
    ]:

        n_obs = len(self.policy.behavior_spec.observation_specs)

        current_obs = ObsUtil.from_buffer(batch, n_obs)
        team_obs = GroupObsUtil.from_buffer(batch, n_obs)

        current_obs = [ModelUtils.list_to_tensor(obs) for obs in current_obs]
        team_obs = [
            [ModelUtils.list_to_tensor(obs) for obs in _teammate_obs]
            for _teammate_obs in team_obs
        ]

        team_actions = AgentAction.group_from_buffer(batch)

        next_obs = [ModelUtils.list_to_tensor(obs) for obs in next_obs]
        next_obs = [obs.unsqueeze(0) for obs in next_obs]

        next_group_obs = [
            ModelUtils.list_to_tensor_list(_list_obs) for _list_obs in next_group_obs
        ]
        # Expand dimensions of next critic obs
        next_group_obs = [
            [_obs.unsqueeze(0) for _obs in _list_obs] for _list_obs in next_group_obs
        ]

        if agent_id in self.value_memory_dict:
            # The agent_id should always be in both since they are added together
            _init_value_mem = self.value_memory_dict[agent_id]
            _init_baseline_mem = self.baseline_memory_dict[agent_id]
        else:
            _init_value_mem = (
                torch.zeros((1, 1, self.critic.memory_size))
                if self.policy.use_recurrent
                else None
            )
            _init_baseline_mem = (
                torch.zeros((1, 1, self.critic.memory_size))
                if self.policy.use_recurrent
                else None
            )

        all_obs = [current_obs] + team_obs if team_obs is not None else [current_obs]
        all_next_value_mem: Optional[AgentBufferField] = None
        all_next_baseline_mem: Optional[AgentBufferField] = None
        if self.policy.use_recurrent:
            (
                value_estimates,
                baseline_estimates,
                all_next_value_mem,
                all_next_baseline_mem,
                next_value_mem,
                next_baseline_mem,
            ) = self._evaluate_by_sequence_team(
                current_obs, team_obs, team_actions, _init_value_mem, _init_baseline_mem
            )
        else:
            value_estimates, next_value_mem = self.critic.critic_pass(
                all_obs, _init_value_mem, sequence_length=batch.num_experiences
            )

            baseline_estimates, next_baseline_mem = self.critic.baseline(
                [current_obs],
                team_obs,
                team_actions,
                _init_baseline_mem,
                sequence_length=batch.num_experiences,
            )
        # Store the memory for the next trajectory
        self.value_memory_dict[agent_id] = next_value_mem
        self.baseline_memory_dict[agent_id] = next_baseline_mem

        all_next_obs = (
            [next_obs] + next_group_obs if next_group_obs is not None else [next_obs]
        )

        next_value_estimates, _ = self.critic.critic_pass(
            all_next_obs, next_value_mem, sequence_length=1
        )

        for name, estimate in baseline_estimates.items():
            baseline_estimates[name] = ModelUtils.to_numpy(estimate)

        for name, estimate in value_estimates.items():
            value_estimates[name] = ModelUtils.to_numpy(estimate)

        # the base line and V shpuld  not be on the same done flag
        for name, estimate in next_value_estimates.items():
            next_value_estimates[name] = ModelUtils.to_numpy(estimate)

        if done:
            for k in next_value_estimates:
                if not self.reward_signals[k].ignore_done:
                    next_value_estimates[k][-1] = 0.0

        return (
            value_estimates,
            baseline_estimates,
            next_value_estimates,
            all_next_value_mem,
            all_next_baseline_mem,
        )
