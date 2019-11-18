# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import (
    Descriptor as google___protobuf___descriptor___Descriptor,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from mlagents.envs.communicator_objects.agent_action_pb2 import (
    AgentActionProto as mlagents___envs___communicator_objects___agent_action_pb2___AgentActionProto,
)

from mlagents.envs.communicator_objects.agent_info_pb2 import (
    AgentInfoProto as mlagents___envs___communicator_objects___agent_info_pb2___AgentInfoProto,
)

from typing import (
    Optional as typing___Optional,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


builtin___bool = bool
builtin___bytes = bytes
builtin___float = float
builtin___int = int


class AgentInfoActionPairProto(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    @property
    def agent_info(self) -> mlagents___envs___communicator_objects___agent_info_pb2___AgentInfoProto: ...

    @property
    def agent_proto(self) -> mlagents___envs___communicator_objects___agent_action_pb2___AgentActionProto: ...

    def __init__(self,
        *,
        agent_info : typing___Optional[mlagents___envs___communicator_objects___agent_info_pb2___AgentInfoProto] = None,
        agent_proto : typing___Optional[mlagents___envs___communicator_objects___agent_action_pb2___AgentActionProto] = None,
        ) -> None: ...
    @classmethod
    def FromString(cls, s: builtin___bytes) -> AgentInfoActionPairProto: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def HasField(self, field_name: typing_extensions___Literal[u"agent_info",u"agent_proto"]) -> builtin___bool: ...
        def ClearField(self, field_name: typing_extensions___Literal[u"agent_info",u"agent_proto"]) -> None: ...
    else:
        def HasField(self, field_name: typing_extensions___Literal[u"agent_info",b"agent_info",u"agent_proto",b"agent_proto"]) -> builtin___bool: ...
        def ClearField(self, field_name: typing_extensions___Literal[u"agent_info",b"agent_info",u"agent_proto",b"agent_proto"]) -> None: ...
