# # Unity ML-Agents Toolkit
import abc
from typing import Any


class BaseSaver(abc.ABC):
    """This class is the base class for the Saver"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def register(self, module: Any) -> None:
        pass

    @abc.abstractmethod
    def save_checkpoint(self, brain_name: str, step: int) -> str:
        """
        Checkpoints the policy on disk.
        :param checkpoint_path: filepath to write the checkpoint
        :param brain_name: Brain name of brain to be trained
        """
        pass

    @abc.abstractmethod
    def export(self, output_filepath: str, brain_name: str) -> None:
        """
        Saves the serialized model, given a path and brain name.
        This method will save the policy graph to the given filepath.  The path
        should be provided without an extension as multiple serialized model formats
        may be generated as a result.
        :param output_filepath: path (without suffix) for the model file(s)
        :param brain_name: Brain name of brain to be trained.
        """
        pass

    @abc.abstractmethod
    def initialize_or_load(self, policy):
        """
        If there is an initialize path, load from that. Else, load from the set model path.
        If load is set to True, don't reset steps to 0. Else, do. This allows a user to,
        e.g., resume from an initialize path.
        """
        pass
