# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: communicator/unity_to_python.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from communicator import unity_initialization_input_pb2 as communicator_dot_unity__initialization__input__pb2
from communicator import unity_initialization_output_pb2 as communicator_dot_unity__initialization__output__pb2
from communicator import unity_input_pb2 as communicator_dot_unity__input__pb2
from communicator import unity_output_pb2 as communicator_dot_unity__output__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='communicator/unity_to_python.proto',
  package='communicator',
  syntax='proto3',
  serialized_pb=_b('\n\"communicator/unity_to_python.proto\x12\x0c\x63ommunicator\x1a-communicator/unity_initialization_input.proto\x1a.communicator/unity_initialization_output.proto\x1a\x1e\x63ommunicator/unity_input.proto\x1a\x1f\x63ommunicator/unity_output.proto2\xaf\x01\n\rUnityToPython\x12_\n\nInitialize\x12\'.communicator.UnityInitializationOutput\x1a&.communicator.UnityInitializationInput\"\x00\x12=\n\x04Send\x12\x19.communicator.UnityOutput\x1a\x18.communicator.UnityInput\"\x00\x42\x18\xaa\x02\x15MLAgents.Communicatorb\x06proto3')
  ,
  dependencies=[communicator_dot_unity__initialization__input__pb2.DESCRIPTOR,communicator_dot_unity__initialization__output__pb2.DESCRIPTOR,communicator_dot_unity__input__pb2.DESCRIPTOR,communicator_dot_unity__output__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\252\002\025MLAgents.Communicator'))

_UNITYTOPYTHON = _descriptor.ServiceDescriptor(
  name='UnityToPython',
  full_name='communicator.UnityToPython',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=213,
  serialized_end=388,
  methods=[
  _descriptor.MethodDescriptor(
    name='Initialize',
    full_name='communicator.UnityToPython.Initialize',
    index=0,
    containing_service=None,
    input_type=communicator_dot_unity__initialization__output__pb2._UNITYINITIALIZATIONOUTPUT,
    output_type=communicator_dot_unity__initialization__input__pb2._UNITYINITIALIZATIONINPUT,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Send',
    full_name='communicator.UnityToPython.Send',
    index=1,
    containing_service=None,
    input_type=communicator_dot_unity__output__pb2._UNITYOUTPUT,
    output_type=communicator_dot_unity__input__pb2._UNITYINPUT,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_UNITYTOPYTHON)

DESCRIPTOR.services_by_name['UnityToPython'] = _UNITYTOPYTHON

# @@protoc_insertion_point(module_scope)
