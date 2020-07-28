import numpy as np

from mlagents.trainers.buffer import AgentBuffer
from mlagents.trainers.reward_providers.base_reward_provider import BaseRewardProvider


class ExtrinsicRewardProvider(BaseRewardProvider):
    def evaluate(self, mini_batch: AgentBuffer) -> np.ndarray:
        return np.array(mini_batch["environment_rewards"], dtype=np.float32)

    def update(self, mini_batch: AgentBuffer) -> None:
        pass
