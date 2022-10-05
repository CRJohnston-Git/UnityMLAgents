import os
from typing import List, Set, Tuple
import numpy as np
from mlagents.trainers.buffer import AgentBuffer, BufferKey
from mlagents_envs.communicator_objects.agent_info_action_pair_pb2 import (
    AgentInfoActionPairProto,
)
from mlagents.trainers.trajectory import ObsUtil
from mlagents_envs.rpc_utils import behavior_spec_from_proto, steps_from_proto
from mlagents_envs.base_env import BehaviorSpec
from mlagents_envs.communicator_objects.brain_parameters_pb2 import BrainParametersProto
from mlagents_envs.communicator_objects.demonstration_meta_pb2 import (
    DemonstrationMetaProto,
)
from mlagents_envs.timers import timed, hierarchical_timer
from mlagents_envs import logging_util
from google.protobuf.internal.decoder import _DecodeVarint32  # type: ignore
from google.protobuf.internal.encoder import _EncodeVarint  # type: ignore


INITIAL_POS = 33
SUPPORTED_DEMONSTRATION_VERSIONS = frozenset([0, 1])

logger = logging_util.get_logger(__name__)


@timed
def make_demo_buffer(
    all_pair_infos: List[List[AgentInfoActionPairProto]],
    behavior_spec: BehaviorSpec,
    sequence_length: int,
) -> AgentBuffer:
    # Create and populate buffer using experiences
    demo_raw_buffer = AgentBuffer()
    demo_processed_buffer = AgentBuffer()
    for pair_infos in all_pair_infos:
        for idx, current_pair_info in enumerate(pair_infos):
            if idx > len(pair_infos) - 2:
                break
            next_pair_info = pair_infos[idx + 1]
            current_decision_step, current_terminal_step = steps_from_proto(
                [current_pair_info.agent_info], behavior_spec
            )
            next_decision_step, next_terminal_step = steps_from_proto(
                [next_pair_info.agent_info], behavior_spec
            )
            previous_action = (
                np.array(
                    pair_infos[idx].action_info.vector_actions_deprecated,
                    dtype=np.float32,
                )
                * 0
            )
            if idx > 0:
                previous_action = np.array(
                    pair_infos[idx - 1].action_info.vector_actions_deprecated,
                    dtype=np.float32,
                )

            next_done = len(next_terminal_step) == 1
            next_reward = 0
            if len(next_terminal_step) == 1:
                next_reward = next_terminal_step.reward[0]
            else:
                next_reward = next_decision_step.reward[0]
            current_obs = None
            if len(current_terminal_step) == 1:
                current_obs = list(current_terminal_step.values())[0].obs
            else:
                current_obs = list(current_decision_step.values())[0].obs

            demo_raw_buffer[BufferKey.DONE].append(next_done)
            demo_raw_buffer[BufferKey.ENVIRONMENT_REWARDS].append(next_reward)
            for i, obs in enumerate(current_obs):
                demo_raw_buffer[ObsUtil.get_name_at(i)].append(obs)
            if (
                len(current_pair_info.action_info.continuous_actions) == 0
                and len(current_pair_info.action_info.discrete_actions) == 0
            ):
                if behavior_spec.action_spec.continuous_size > 0:
                    demo_raw_buffer[BufferKey.CONTINUOUS_ACTION].append(
                        current_pair_info.action_info.vector_actions_deprecated
                    )
                else:
                    demo_raw_buffer[BufferKey.DISCRETE_ACTION].append(
                        current_pair_info.action_info.vector_actions_deprecated
                    )
            else:
                if behavior_spec.action_spec.continuous_size > 0:
                    demo_raw_buffer[BufferKey.CONTINUOUS_ACTION].append(
                        current_pair_info.action_info.continuous_actions
                    )
                if behavior_spec.action_spec.discrete_size > 0:
                    demo_raw_buffer[BufferKey.DISCRETE_ACTION].append(
                        current_pair_info.action_info.discrete_actions
                    )
            demo_raw_buffer[BufferKey.PREV_ACTION].append(previous_action)
            if next_done:
                demo_raw_buffer.resequence_and_append(
                    demo_processed_buffer,
                    batch_size=None,
                    training_length=sequence_length,
                )
                demo_raw_buffer.reset_agent()
    demo_raw_buffer.resequence_and_append(
        demo_processed_buffer, batch_size=None, training_length=sequence_length
    )
    return demo_processed_buffer


@timed
def demo_to_buffer(
    file_path: str, sequence_length: int, expected_behavior_spec: BehaviorSpec = None
) -> Tuple[BehaviorSpec, AgentBuffer, List[str]]:
    """
    Loads demonstration file and uses it to fill training buffer.
    :param file_path: Location of demonstration file (.demo).
    :param sequence_length: Length of trajectories to fill buffer.
    :return:
    """
    behavior_spec, info_action_pairs, file_paths = load_demonstration(file_path)
    if len(file_paths) == 0:
        return None, AgentBuffer(), file_paths
    demo_buffer = make_demo_buffer(info_action_pairs, behavior_spec, sequence_length)
    if expected_behavior_spec:
        # check action dimensions in demonstration match
        if behavior_spec.action_spec != expected_behavior_spec.action_spec:
            raise RuntimeError(
                "The actions {} in demonstration do not match the policy's {}.".format(
                    behavior_spec.action_spec, expected_behavior_spec.action_spec
                )
            )
        # check observations match
        if len(behavior_spec.observation_specs) != len(
            expected_behavior_spec.observation_specs
        ):
            raise RuntimeError(
                "The demonstrations do not have the same number of observations as the policy."
            )
        else:
            for i, (demo_obs, policy_obs) in enumerate(
                zip(
                    behavior_spec.observation_specs,
                    expected_behavior_spec.observation_specs,
                )
            ):
                if demo_obs.shape != policy_obs.shape:
                    raise RuntimeError(
                        f"The shape {demo_obs} for observation {i} in demonstration \
                        do not match the policy's {policy_obs}."
                    )
    return behavior_spec, demo_buffer, file_paths


def get_demo_files(path: str) -> List[str]:
    """
    Retrieves the demonstration file(s) from a path.
    :param path: Path of demonstration file or directory.
    :return: List of demonstration files

    Raises errors if |path| is invalid.
    """
    if os.path.isfile(path):
        if not path.endswith(".demo"):
            raise ValueError("The path provided is not a '.demo' file.")
        return [path]
    elif os.path.isdir(path):
        paths = [
            os.path.join(path, name)
            for name in os.listdir(path)
            if name.endswith(".demo")
        ]
        if not paths:
            logger.debug("There are no '.demo' files in the provided directory.")
        return paths
    else:
        raise FileNotFoundError(
            f"The demonstration file or directory {path} does not exist."
        )


@timed
def load_demonstration(
    file_path: str, exclusions: set = None
) -> Tuple[BehaviorSpec, List[AgentInfoActionPairProto], List[str]]:
    """
    Loads and parses a demonstration file.
    :param file_path: Location of demonstration file (.demo).
    :return: BrainParameter and list of AgentInfoActionPairProto containing demonstration data.
    """

    # First 32 bytes of file dedicated to meta-data.
    file_paths = set(get_demo_files(file_path))
    if exclusions is not None:
        file_paths = file_paths - exclusions
    behavior_spec = None
    brain_param_proto = None
    total_expected = 0
    # We divide it up in files so that we don't accidentally merge them
    info_action_pairs: List[List[AgentInfoActionPairProto]] = []
    for _file_path in file_paths:
        with open(_file_path, "rb") as fp:
            expected_in_file = 0
            _info_pairs_per_file = []
            with hierarchical_timer("read_file"):
                data = fp.read()
            next_pos, pos, obs_decoded = 0, 0, 0
            while pos < len(data):
                next_pos, pos = _DecodeVarint32(data, pos)
                if obs_decoded == 0:
                    meta_data_proto = DemonstrationMetaProto()
                    meta_data_proto.ParseFromString(data[pos : pos + next_pos])
                    if (
                        meta_data_proto.api_version
                        not in SUPPORTED_DEMONSTRATION_VERSIONS
                    ):
                        raise RuntimeError(
                            f"Can't load Demonstration data from an unsupported version \
                                ({meta_data_proto.api_version})"
                        )
                    expected_in_file += meta_data_proto.number_steps
                    pos = INITIAL_POS
                if obs_decoded == 1:
                    brain_param_proto = BrainParametersProto()
                    brain_param_proto.ParseFromString(data[pos : pos + next_pos])
                    pos += next_pos
                if obs_decoded > 1:
                    agent_info_action = AgentInfoActionPairProto()
                    agent_info_action.ParseFromString(data[pos : pos + next_pos])
                    if behavior_spec is None:
                        behavior_spec = behavior_spec_from_proto(
                            brain_param_proto, agent_info_action.agent_info
                        )
                    _info_pairs_per_file.append(agent_info_action)
                    if len(_info_pairs_per_file) == expected_in_file:
                        break
                    pos += next_pos
                obs_decoded += 1
        info_action_pairs.append(_info_pairs_per_file)
        total_expected += expected_in_file
    if not behavior_spec and total_expected > 0:
        raise RuntimeError(
            f"No BrainParameters found in demonstration file at {file_path}."
        )
    return behavior_spec, info_action_pairs, list(file_paths)


def write_delimited(f, message):
    msg_string = message.SerializeToString()
    msg_size = len(msg_string)
    _EncodeVarint(f.write, msg_size)
    f.write(msg_string)


def write_demo(demo_path, meta_data_proto, brain_param_proto, agent_info_protos):
    with open(demo_path, "wb") as f:
        # write metadata
        write_delimited(f, meta_data_proto)
        f.seek(INITIAL_POS)
        write_delimited(f, brain_param_proto)

        for agent in agent_info_protos:
            write_delimited(f, agent)


class DemoManager:
    def __init__(
        self,
        path: str,
        sequence_length: int = 1,
        expected_bspec: BehaviorSpec = None,
        demo_buffer_size: int = 1000000,
    ) -> None:
        self.path = path
        self._seq_len = sequence_length
        self._loaded_files: Set[str] = set()
        _, self._demo_buffer, file_paths = demo_to_buffer(
            path, sequence_length, expected_bspec
        )
        self._loaded_files.update(file_paths)
        self._max_demo_buffer_size = demo_buffer_size
        if len(file_paths) == 0:
            self._demo_buffer = AgentBuffer()
            logger.warn(f"No demos found in {path}. Continuing to look for new files.")

    @property
    def demo_buffer(self) -> AgentBuffer:
        return self._demo_buffer

    def refresh(self) -> int:
        bspec, loaded_demos, loaded_paths = load_demonstration(
            self.path, self._loaded_files
        )
        if loaded_paths:
            new_demos = make_demo_buffer(loaded_demos, bspec, self._seq_len)
            new_demos.resequence_and_append(
                self._demo_buffer, training_length=self._seq_len
            )
            self._loaded_files.update(loaded_paths)
            num_new_exp = new_demos.num_experiences
            if self._demo_buffer.num_experiences > self._max_demo_buffer_size:
                self._demo_buffer.truncate(
                    int(self._max_demo_buffer_size * 0.8), self._seq_len
                )
            return num_new_exp
        else:
            return 0
