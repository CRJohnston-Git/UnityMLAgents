from typing import Any, Dict, List, Tuple, Optional
import numpy as np
from mlagents.torch_utils import torch, default_device
import copy

from mlagents.trainers.action_info import ActionInfo
from mlagents.trainers.behavior_id_utils import get_global_agent_id
from mlagents.trainers.policy import Policy
from mlagents_envs.base_env import DecisionSteps, BehaviorSpec
from mlagents_envs.timers import timed

from mlagents.trainers.settings import TrainerSettings
from mlagents.trainers.trajectory import SplitObservations
from mlagents.trainers.torch.networks import (
    SharedActorCritic,
    SeparateActorCritic,
    GlobalSteps,
)
from mlagents.trainers.torch.utils import ModelUtils

EPSILON = 1e-7  # Small value to avoid divide by zero


class TorchPolicy(Policy):
    def __init__(
        self,
        seed: int,
        behavior_spec: BehaviorSpec,
        trainer_settings: TrainerSettings,
        tanh_squash: bool = False,
        reparameterize: bool = False,
        separate_critic: bool = True,
        condition_sigma_on_obs: bool = True,
    ):
        """
        Policy that uses a multilayer perceptron to map the observations to actions. Could
        also use a CNN to encode visual input prior to the MLP. Supports discrete and
        continuous action spaces, as well as recurrent networks.
        :param seed: Random seed.
        :param behavior_spec: Assigned BehaviorSpec object.
        :param trainer_settings: Defined training parameters.
        :param load: Whether a pre-trained model will be loaded or a new one created.
        :param tanh_squash: Whether to use a tanh function on the continuous output,
        or a clipped output.
        :param reparameterize: Whether we are using the resampling trick to update the policy
        in continuous output.
        """
        super().__init__(
            seed,
            behavior_spec,
            trainer_settings,
            tanh_squash,
            reparameterize,
            condition_sigma_on_obs,
        )
        self.global_step = (
            GlobalSteps()
        )  # could be much simpler if TorchPolicy is nn.Module
        self.grads = None

        reward_signal_configs = trainer_settings.reward_signals
        reward_signal_names = [key.value for key, _ in reward_signal_configs.items()]

        self.stats_name_to_update_name = {
            "Losses/Value Loss": "value_loss",
            "Losses/Policy Loss": "policy_loss",
        }
        if separate_critic:
            ac_class = SeparateActorCritic
        else:
            ac_class = SharedActorCritic
        self.actor_critic = ac_class(
            observation_shapes=self.behavior_spec.observation_shapes,
            network_settings=trainer_settings.network_settings,
            act_type=behavior_spec.action_type,
            continuous_act_size=self.continuous_act_size,
            discrete_act_size=self.discrete_act_size,
            stream_names=reward_signal_names,
            conditional_sigma=self.condition_sigma_on_obs,
            tanh_squash=tanh_squash,
        )
        # Save the m_size needed for export
        self._export_m_size = self.m_size
        # m_size needed for training is determined by network, not trainer settings
        self.m_size = self.actor_critic.memory_size

        self.actor_critic.to(default_device())

    @property
    def export_memory_size(self) -> int:
        """
        Returns the memory size of the exported ONNX policy. This only includes the memory
        of the Actor and not any auxillary networks.
        """
        return self._export_m_size

    def _split_decision_step(
        self, decision_requests: DecisionSteps
    ) -> Tuple[SplitObservations, np.ndarray]:
        vec_vis_obs = SplitObservations.from_observations(decision_requests.obs)
        mask = None
        if not self.use_continuous_act:
            mask = torch.ones([len(decision_requests), np.sum(self.act_size)])
            if decision_requests.action_mask is not None:
                mask = torch.as_tensor(
                    1 - np.concatenate(decision_requests.action_mask, axis=1)
                )
        return vec_vis_obs, mask

    def update_normalization(self, vector_obs: np.ndarray) -> None:
        """
        If this policy normalizes vector observations, this will update the norm values in the graph.
        :param vector_obs: The vector observations to add to the running estimate of the distribution.
        """
        vector_obs = [torch.as_tensor(vector_obs)]
        if self.use_vec_obs and self.normalize:
            self.actor_critic.update_normalization(vector_obs)

    def get_actions_and_stats(dists : List[DistInstance]):
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        action_list = self.actor_critic.sample_action(dists)
        log_probs, entropies, all_logs = ModelUtils.get_probs_and_entropy(
            action_list, dists
        )
        actions = torch.stack(action_list, dim=-1)
        return (
            actions,
            all_logs if all_log_probs else log_probs,
            entropies,
        )


    @timed
    def sample_actions(
        self,
        vec_obs: List[torch.Tensor],
        vis_obs: List[torch.Tensor],
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        seq_len: int = 1,
        all_log_probs: bool = False,
    ) -> Tuple[
        torch.Tensor, torch.Tensor, torch.Tensor, Dict[str, torch.Tensor], torch.Tensor
    ]:
        """
        :param all_log_probs: Returns (for discrete actions) a tensor of log probs, one for each action.
        """
        continuous_dists, discrete_dists, value_heads, memories = self.actor_critic.get_dist_and_value(
            vec_obs, vis_obs, masks, memories, seq_len
        )
        continuous_actions, continuous_entropies, continuous_log_probs = self.get_action_and_stats(continuous_dists) 
        discrete_actions, discrete_entropies, discrete_log_probs = self.get_action_and_stats(discrete_dists) 
        continuous_actions = continuous_actions[:, :, 0]
        discrete_actions = discrete_actions[:, 0, :]

        return (
            continuous_actions,
            continuous_log_probs,
            continuous_entropies,
            discrete_actions,
            discrete_log_probs,
            discrete_entropies,
            value_heads,
            memories,
        )

    def evaluate_actions(
        self,
        vec_obs: torch.Tensor,
        vis_obs: torch.Tensor,
        continuous_actions: torch.Tensor,
        discrete_actions: torch.Tensor,
        masks: Optional[torch.Tensor] = None,
        memories: Optional[torch.Tensor] = None,
        seq_len: int = 1,
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict[str, torch.Tensor]]:
        continuous_dists, discrete_dists, value_heads, memories = self.actor_critic.get_dist_and_value(
            vec_obs, vis_obs, masks, memories, seq_len
        )
        continuous_action_list = [actions[..., i] for i in range(actions.shape[-1])]
        discrete_action_list = [actions[..., i] for i in range(actions.shape[-1])]
        continuous_log_probs, continuous_entropies, _ = ModelUtils.get_probs_and_entropy(continuous_action_list, dists)
        discrete_log_probs, discrete_entropies, _ = ModelUtils.get_probs_and_entropy(discrete_action_list, dists)

        return continuous_log_probs, continuous_entropies, discrete_log_probs, discrete_entropies, value_heads

    @timed
    def evaluate(
        self, decision_requests: DecisionSteps, global_agent_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates policy for the agent experiences provided.
        :param global_agent_ids:
        :param decision_requests: DecisionStep object containing inputs.
        :return: Outputs from network as defined by self.inference_dict.
        """
        vec_vis_obs, masks = self._split_decision_step(decision_requests)
        vec_obs = [torch.as_tensor(vec_vis_obs.vector_observations)]
        vis_obs = [
            torch.as_tensor(vis_ob) for vis_ob in vec_vis_obs.visual_observations
        ]
        memories = torch.as_tensor(self.retrieve_memories(global_agent_ids)).unsqueeze(
            0
        )

        run_out = {}
        with torch.no_grad():
            continuous_action, continuous_log_probs, continuous_entropy, discrete_action, discrete_log_probs, discrete_entropy, value_heads, memories = self.sample_actions(
                vec_obs, vis_obs, masks=masks, memories=memories
            )
        # Todo - make pre_action difference
        run_out["pre_action"] = ModelUtils.to_numpy(action)
        run_out["continuous_action"] = ModelUtils.to_numpy(continuous_action)
        run_out["continuous_log_probs"] = ModelUtils.to_numpy(log_probs)
        run_out["continuous_entropy"] = ModelUtils.to_numpy(entropy)
        run_out["discrete_action"] = ModelUtils.to_numpy(discrete_action)
        run_out["discrete_log_probs"] = ModelUtils.to_numpy(log_probs)
        run_out["discrete_entropy"] = ModelUtils.to_numpy(entropy)

        run_out["value_heads"] = {
            name: ModelUtils.to_numpy(t) for name, t in value_heads.items()
        }
        run_out["value"] = np.mean(list(run_out["value_heads"].values()), 0)
        run_out["learning_rate"] = 0.0
        if self.use_recurrent:
            run_out["memory_out"] = ModelUtils.to_numpy(memories).squeeze(0)
        return run_out

    def get_action(
        self, decision_requests: DecisionSteps, worker_id: int = 0
    ) -> ActionInfo:
        """
        Decides actions given observations information, and takes them in environment.
        :param worker_id:
        :param decision_requests: A dictionary of behavior names and DecisionSteps from environment.
        :return: an ActionInfo containing action, memories, values and an object
        to be passed to add experiences
        """
        if len(decision_requests) == 0:
            return ActionInfo.empty()

        global_agent_ids = [
            get_global_agent_id(worker_id, int(agent_id))
            for agent_id in decision_requests.agent_id
        ]  # For 1-D array, the iterator order is correct.

        run_out = self.evaluate(
            decision_requests, global_agent_ids
        )  # pylint: disable=assignment-from-no-return
        self.save_memories(global_agent_ids, run_out.get("memory_out"))
        action = np.concat([run_out.get("continuous_action"), run_out.get("discrete_action")], axis=1)
        return ActionInfo(
            action=action,
            value=run_out.get("value"),
            outputs=run_out,
            agent_ids=list(decision_requests.agent_id),
        )

    @property
    def use_vis_obs(self):
        return self.vis_obs_size > 0

    @property
    def use_vec_obs(self):
        return self.vec_obs_size > 0

    def get_current_step(self):
        """
        Gets current model step.
        :return: current model step.
        """
        return self.global_step.current_step

    def set_step(self, step: int) -> int:
        """
        Sets current model step to step without creating additional ops.
        :param step: Step to set the current model step to.
        :return: The step the model was set to.
        """
        self.global_step.current_step = step
        return step

    def increment_step(self, n_steps):
        """
        Increments model step.
        """
        self.global_step.increment(n_steps)
        return self.get_current_step()

    def load_weights(self, values: List[np.ndarray]) -> None:
        self.actor_critic.load_state_dict(values)

    def init_load_weights(self) -> None:
        pass

    def get_weights(self) -> List[np.ndarray]:
        return copy.deepcopy(self.actor_critic.state_dict())

    def get_modules(self):
        return {"Policy": self.actor_critic, "global_step": self.global_step}
