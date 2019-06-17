import unittest.mock as mock
import pytest
import mlagents.trainers.tests.mock_brain as mb

import numpy as np
import tensorflow as tf
import yaml
import os

from mlagents.trainers.ppo.models import PPOModel
from mlagents.trainers.ppo.trainer import discount_rewards
from mlagents.trainers.ppo.policy import PPOPolicy
from mlagents.envs import UnityEnvironment
from mlagents.envs.mock_communicator import MockCommunicator


@pytest.fixture
def dummy_config():
    return yaml.safe_load(
        """
        trainer: ppo
        batch_size: 32
        beta: 5.0e-3
        buffer_size: 512
        epsilon: 0.2
        hidden_units: 128
        lambd: 0.95
        learning_rate: 3.0e-4
        max_steps: 5.0e4
        normalize: true
        num_epoch: 5
        num_layers: 2
        time_horizon: 64
        sequence_length: 64
        summary_freq: 1000
        use_recurrent: false
        memory_size: 8
        curiosity_strength: 0.0
        curiosity_enc_size: 1
        reward_signals:
          extrinsic:
            strength: 1.0
            gamma: 0.99
        """
    )


@pytest.fixture
def curiosity_dummy_config():
    return {"curiosity": {"strength": 0.1, "gamma": 0.9, "encoding_size": 128}}


def create_ppo_policy_mock(
    mock_env, dummy_config, reward_signal_config, use_rnn, use_discrete, use_visual
):

    if not use_visual:
        mock_brain = mb.create_mock_brainparams(
            vector_action_space_type="discrete" if use_discrete else "continuous",
            vector_action_space_size=[2],
            vector_observation_space_size=8,
        )
        mock_braininfo = mb.create_mock_braininfo(
            num_agents=12,
            num_vector_observations=8,
            num_vector_acts=2,
            discrete=use_discrete,
        )
    else:
        mock_brain = mb.create_mock_brainparams(
            vector_action_space_type="discrete" if use_discrete else "continuous",
            vector_action_space_size=[2],
            vector_observation_space_size=0,
            number_visual_observations=1,
        )
        mock_braininfo = mb.create_mock_braininfo(
            num_agents=12,
            num_vis_observations=1,
            num_vector_acts=2,
            discrete=use_discrete,
        )
    mb.setup_mock_unityenvironment(mock_env, mock_brain, mock_braininfo)
    env = mock_env()

    trainer_parameters = dummy_config
    model_path = env.brain_names[0]
    trainer_parameters["model_path"] = model_path
    trainer_parameters["keep_checkpoints"] = 3
    trainer_parameters["reward_signals"].update(reward_signal_config)
    trainer_parameters["use_recurrent"] = use_rnn
    policy = PPOPolicy(0, mock_brain, trainer_parameters, False, False)
    return env, policy


@mock.patch("mlagents.envs.UnityEnvironment")
def test_curiosity_cc_evaluate(mock_env, dummy_config, curiosity_dummy_config):
    env, policy = create_ppo_policy_mock(
        mock_env, dummy_config, curiosity_dummy_config, False, False, False
    )
    brain_infos = env.reset()
    brain_info = brain_infos[env.brain_names[0]]
    next_brain_info = env.step()[env.brain_names[0]]
    scaled_reward, unscaled_reward = policy.reward_signals["curiosity"].evaluate(
        brain_info, next_brain_info
    )
    assert scaled_reward.shape == (12,)
    assert unscaled_reward.shape == (12,)


@mock.patch("mlagents.envs.UnityEnvironment")
def test_curiosity_dc_evaluate(mock_env, dummy_config, curiosity_dummy_config):
    env, policy = create_ppo_policy_mock(
        mock_env, dummy_config, curiosity_dummy_config, False, True, False
    )
    brain_infos = env.reset()
    brain_info = brain_infos[env.brain_names[0]]
    next_brain_info = env.step()[env.brain_names[0]]
    scaled_reward, unscaled_reward = policy.reward_signals["curiosity"].evaluate(
        brain_info, next_brain_info
    )
    assert scaled_reward.shape == (12,)
    assert unscaled_reward.shape == (12,)


@mock.patch("mlagents.envs.UnityEnvironment")
def test_curiosity_visual_evaluate(mock_env, dummy_config, curiosity_dummy_config):
    env, policy = create_ppo_policy_mock(
        mock_env, dummy_config, curiosity_dummy_config, False, False, True
    )
    brain_infos = env.reset()
    brain_info = brain_infos[env.brain_names[0]]
    next_brain_info = env.step()[env.brain_names[0]]
    scaled_reward, unscaled_reward = policy.reward_signals["curiosity"].evaluate(
        brain_info, next_brain_info
    )
    assert scaled_reward.shape == (12,)
    assert unscaled_reward.shape == (12,)


@mock.patch("mlagents.envs.UnityEnvironment")
def test_curiosity_rnn_evaluate(mock_env, dummy_config, curiosity_dummy_config):
    env, policy = create_ppo_policy_mock(
        mock_env, dummy_config, curiosity_dummy_config, True, False, False
    )
    brain_infos = env.reset()
    brain_info = brain_infos[env.brain_names[0]]
    next_brain_info = env.step()[env.brain_names[0]]
    scaled_reward, unscaled_reward = policy.reward_signals["curiosity"].evaluate(
        brain_info, next_brain_info
    )
    assert scaled_reward.shape == (12,)
    assert unscaled_reward.shape == (12,)


if __name__ == "__main__":
    pytest.main()
