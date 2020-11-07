import attr


from mlagents.trainers.tests.simple_test_envs import (
    SimpleEnvironment,
    MemoryEnvironment,
)

from mlagents.trainers.settings import NetworkSettings, FrameworkType

from mlagents.trainers.tests.dummy_config import ppo_dummy_config, sac_dummy_config
from mlagents.trainers.tests.check_env_trains import check_environment_trains

BRAIN_NAME = "1D"

PPO_TORCH_CONFIG = attr.evolve(ppo_dummy_config(), framework=FrameworkType.PYTORCH)
SAC_TORCH_CONFIG = attr.evolve(sac_dummy_config(), framework=FrameworkType.PYTORCH)


def test_recurrent_ppo():
    env = MemoryEnvironment(
        [BRAIN_NAME], continuous_action_size=1, discrete_action_size=1
    )
    new_network_settings = attr.evolve(
        PPO_TORCH_CONFIG.network_settings,
        memory=NetworkSettings.MemorySettings(memory_size=16),
    )
    new_hyperparams = attr.evolve(
        PPO_TORCH_CONFIG.hyperparameters,
        learning_rate=1.0e-3,
        batch_size=64,
        buffer_size=128,
    )
    config = attr.evolve(
        PPO_TORCH_CONFIG,
        hyperparameters=new_hyperparams,
        network_settings=new_network_settings,
        max_steps=5000,
    )
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=0.9)


def test_hybrid_ppo():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=1, discrete_action_size=1, step_size=0.8
    )
    new_hyperparams = attr.evolve(
        PPO_TORCH_CONFIG.hyperparameters, batch_size=32, buffer_size=1280
    )
    config = attr.evolve(
        PPO_TORCH_CONFIG, hyperparameters=new_hyperparams, max_steps=10000
    )
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_conthybrid_ppo():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=1, discrete_action_size=0, step_size=0.8
    )
    config = attr.evolve(PPO_TORCH_CONFIG)
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_dischybrid_ppo():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=0, discrete_action_size=1, step_size=0.8
    )
    config = attr.evolve(PPO_TORCH_CONFIG)
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_3cdhybrid_ppo():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=2, discrete_action_size=1, step_size=0.8
    )
    new_hyperparams = attr.evolve(
        PPO_TORCH_CONFIG.hyperparameters, batch_size=128, buffer_size=1280, beta=0.01
    )
    config = attr.evolve(
        PPO_TORCH_CONFIG, hyperparameters=new_hyperparams, max_steps=10000
    )
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_3ddhybrid_ppo():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=1, discrete_action_size=2, step_size=0.8
    )
    new_hyperparams = attr.evolve(
        PPO_TORCH_CONFIG.hyperparameters, batch_size=128, buffer_size=1280, beta=0.01
    )
    config = attr.evolve(
        PPO_TORCH_CONFIG, hyperparameters=new_hyperparams, max_steps=10000
    )
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_hybrid_sac():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=1, discrete_action_size=1, step_size=0.8
    )
    new_hyperparams = attr.evolve(
        SAC_TORCH_CONFIG.hyperparameters, buffer_size=50000, batch_size=128
    )
    config = attr.evolve(
        SAC_TORCH_CONFIG, hyperparameters=new_hyperparams, max_steps=10000
    )
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_conthybrid_sac():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=1, discrete_action_size=0, step_size=0.8
    )
    config = attr.evolve(SAC_TORCH_CONFIG)
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_dischybrid_sac():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=0, discrete_action_size=1, step_size=0.8
    )
    config = attr.evolve(SAC_TORCH_CONFIG)
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_3chybrid_sac():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=2, discrete_action_size=1, step_size=0.8
    )
    new_hyperparams = attr.evolve(
        SAC_TORCH_CONFIG.hyperparameters, batch_size=128, buffer_size=50000
    )
    config = attr.evolve(
        SAC_TORCH_CONFIG, hyperparameters=new_hyperparams, max_steps=10000
    )
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)


def test_3ddhybrid_sac():
    env = SimpleEnvironment(
        [BRAIN_NAME], continuous_action_size=1, discrete_action_size=2, step_size=0.8
    )
    new_hyperparams = attr.evolve(
        SAC_TORCH_CONFIG.hyperparameters, batch_size=128, buffer_size=50000
    )
    config = attr.evolve(
        SAC_TORCH_CONFIG, hyperparameters=new_hyperparams, max_steps=10000
    )
    check_environment_trains(env, {BRAIN_NAME: config}, success_threshold=1.0)
