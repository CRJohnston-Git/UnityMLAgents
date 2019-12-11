# # Unity ML-Agents Toolkit
# ## ML-Agent Learning (Behavioral Cloning)
# Contains an implementation of Behavioral Cloning Algorithm

import logging

import numpy as np
from collections import defaultdict

from mlagents.trainers.bc.policy import BCPolicy
from mlagents.trainers.buffer import AgentBuffer
from mlagents.trainers.trajectory import Trajectory
from mlagents.trainers.trainer import Trainer

logger = logging.getLogger("mlagents.trainers")


class BCTrainer(Trainer):
    """The BCTrainer is an implementation of Behavioral Cloning."""

    def __init__(self, brain, trainer_parameters, training, load, seed, run_id):
        """
        Responsible for collecting experiences and training PPO model.
        :param  trainer_parameters: The parameters for the trainer (dictionary).
        :param training: Whether the trainer is set for training.
        :param load: Whether the model should be loaded.
        :param seed: The seed the model will be initialized with
        :param run_id: The identifier of the current run
        """
        super(BCTrainer, self).__init__(brain, trainer_parameters, training, run_id)
        self.policy = BCPolicy(seed, brain, trainer_parameters, load)
        self.n_sequences = 1
        self.cumulative_rewards = defaultdict(lambda: 0)
        self.episode_steps = {}
        self.stats = {
            "Losses/Cloning Loss": [],
            "Environment/Episode Length": [],
            "Environment/Cumulative Reward": [],
        }

        self.batches_per_epoch = trainer_parameters["batches_per_epoch"]

        self.demonstration_buffer = AgentBuffer()

    def process_trajectory(self, trajectory: Trajectory) -> None:
        """
        Takes a trajectory and processes it, putting it into the update buffer.
        Processing involves calculating value and advantage targets for model updating step.
        """
        agent_id = trajectory.agent_id  # All the experiences should have the same ID
        agent_buffer_trajectory = trajectory.to_agentbuffer()

        # Evaluate all reward functions
        self.cumulative_rewards[agent_id] += np.sum(
            agent_buffer_trajectory["environment_rewards"]
        )

        # Increment episode steps
        if agent_id not in self.episode_steps:
            self.episode_steps[agent_id] = 0
        else:
            self.episode_steps[agent_id] += len(trajectory.steps)

        if trajectory.done_reached:
            self.stats["Environment/Episode Length"].append(
                self.episode_steps.get(agent_id, 0)
            )
            self.episode_steps[agent_id] = 0

            self.cumulative_returns_since_policy_update.append(
                self.cumulative_rewards.get(agent_id, 0)
            )
            self.stats["Environment/Cumulative Reward"].append(
                self.cumulative_rewards.get(agent_id, 0)
            )
            self.cumulative_rewards[agent_id] = 0

    def end_episode(self):
        """
        A signal that the Episode has ended. The buffer must be reset.
        Get only called when the academy resets.
        """
        for agent_id in self.cumulative_rewards:
            self.cumulative_rewards[agent_id] = 0
        for agent_id in self.episode_steps:
            self.episode_steps[agent_id] = 0

    def is_ready_update(self):
        """
        Returns whether or not the trainer has enough elements to run update model
        :return: A boolean corresponding to whether or not update_model() can be run
        """
        return self.demonstration_buffer.num_experiences > self.n_sequences

    def update_policy(self):
        """
        Updates the policy.
        """
        self.demonstration_buffer.shuffle(self.policy.sequence_length)
        batch_losses = []
        batch_size = self.n_sequences * self.policy.sequence_length
        # We either divide the entire buffer into num_batches batches, or limit the number
        # of batches to batches_per_epoch.
        num_batches = min(
            self.demonstration_buffer.num_experiences // batch_size,
            self.batches_per_epoch,
        )

        for i in range(0, num_batches * batch_size, batch_size):
            update_buffer = self.demonstration_buffer
            mini_batch = update_buffer.make_mini_batch(i, i + batch_size)
            run_out = self.policy.update(mini_batch, self.n_sequences)
            loss = run_out["policy_loss"]
            batch_losses.append(loss)
        if len(batch_losses) > 0:
            self.stats["Losses/Cloning Loss"].append(np.mean(batch_losses))
        else:
            self.stats["Losses/Cloning Loss"].append(0)
