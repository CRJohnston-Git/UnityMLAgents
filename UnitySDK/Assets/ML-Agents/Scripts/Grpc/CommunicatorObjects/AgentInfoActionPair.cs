// <auto-generated>
//     Generated by the protocol buffer compiler.  DO NOT EDIT!
//     source: mlagents/envs/communicator_objects/agent_info_action_pair.proto
// </auto-generated>
#pragma warning disable 1591, 0612, 3021
#region Designer generated code

using pb = global::Google.Protobuf;
using pbc = global::Google.Protobuf.Collections;
using pbr = global::Google.Protobuf.Reflection;
using scg = global::System.Collections.Generic;
namespace MLAgents.CommunicatorObjects {

  /// <summary>Holder for reflection information generated from mlagents/envs/communicator_objects/agent_info_action_pair.proto</summary>
  public static partial class AgentInfoActionPairReflection {

    #region Descriptor
    /// <summary>File descriptor for mlagents/envs/communicator_objects/agent_info_action_pair.proto</summary>
    public static pbr::FileDescriptor Descriptor {
      get { return descriptor; }
    }
    private static pbr::FileDescriptor descriptor;

    static AgentInfoActionPairReflection() {
      byte[] descriptorData = global::System.Convert.FromBase64String(
          string.Concat(
            "Cj9tbGFnZW50cy9lbnZzL2NvbW11bmljYXRvcl9vYmplY3RzL2FnZW50X2lu",
            "Zm9fYWN0aW9uX3BhaXIucHJvdG8SFGNvbW11bmljYXRvcl9vYmplY3RzGjNt",
            "bGFnZW50cy9lbnZzL2NvbW11bmljYXRvcl9vYmplY3RzL2FnZW50X2luZm8u",
            "cHJvdG8aNW1sYWdlbnRzL2VudnMvY29tbXVuaWNhdG9yX29iamVjdHMvYWdl",
            "bnRfYWN0aW9uLnByb3RvIpEBChhBZ2VudEluZm9BY3Rpb25QYWlyUHJvdG8S",
            "OAoKYWdlbnRfaW5mbxgBIAEoCzIkLmNvbW11bmljYXRvcl9vYmplY3RzLkFn",
            "ZW50SW5mb1Byb3RvEjsKC2FnZW50X3Byb3RvGAIgASgLMiYuY29tbXVuaWNh",
            "dG9yX29iamVjdHMuQWdlbnRBY3Rpb25Qcm90b0IfqgIcTUxBZ2VudHMuQ29t",
            "bXVuaWNhdG9yT2JqZWN0c2IGcHJvdG8z"));
      descriptor = pbr::FileDescriptor.FromGeneratedCode(descriptorData,
          new pbr::FileDescriptor[] { global::MLAgents.CommunicatorObjects.AgentInfoReflection.Descriptor, global::MLAgents.CommunicatorObjects.AgentActionReflection.Descriptor, },
          new pbr::GeneratedClrTypeInfo(null, new pbr::GeneratedClrTypeInfo[] {
            new pbr::GeneratedClrTypeInfo(typeof(global::MLAgents.CommunicatorObjects.AgentInfoActionPairProto), global::MLAgents.CommunicatorObjects.AgentInfoActionPairProto.Parser, new[]{ "AgentInfo", "AgentProto" }, null, null, null)
          }));
    }
    #endregion

  }
  #region Messages
  public sealed partial class AgentInfoActionPairProto : pb::IMessage<AgentInfoActionPairProto> {
    private static readonly pb::MessageParser<AgentInfoActionPairProto> _parser = new pb::MessageParser<AgentInfoActionPairProto>(() => new AgentInfoActionPairProto());
    private pb::UnknownFieldSet _unknownFields;
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public static pb::MessageParser<AgentInfoActionPairProto> Parser { get { return _parser; } }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public static pbr::MessageDescriptor Descriptor {
      get { return global::MLAgents.CommunicatorObjects.AgentInfoActionPairReflection.Descriptor.MessageTypes[0]; }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    pbr::MessageDescriptor pb::IMessage.Descriptor {
      get { return Descriptor; }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public AgentInfoActionPairProto() {
      OnConstruction();
    }

    partial void OnConstruction();

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public AgentInfoActionPairProto(AgentInfoActionPairProto other) : this() {
      AgentInfo = other.agentInfo_ != null ? other.AgentInfo.Clone() : null;
      AgentProto = other.agentProto_ != null ? other.AgentProto.Clone() : null;
      _unknownFields = pb::UnknownFieldSet.Clone(other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public AgentInfoActionPairProto Clone() {
      return new AgentInfoActionPairProto(this);
    }

    /// <summary>Field number for the "agent_info" field.</summary>
    public const int AgentInfoFieldNumber = 1;
    private global::MLAgents.CommunicatorObjects.AgentInfoProto agentInfo_;
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public global::MLAgents.CommunicatorObjects.AgentInfoProto AgentInfo {
      get { return agentInfo_; }
      set {
        agentInfo_ = value;
      }
    }

    /// <summary>Field number for the "agent_proto" field.</summary>
    public const int AgentProtoFieldNumber = 2;
    private global::MLAgents.CommunicatorObjects.AgentActionProto agentProto_;
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public global::MLAgents.CommunicatorObjects.AgentActionProto AgentProto {
      get { return agentProto_; }
      set {
        agentProto_ = value;
      }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public override bool Equals(object other) {
      return Equals(other as AgentInfoActionPairProto);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public bool Equals(AgentInfoActionPairProto other) {
      if (ReferenceEquals(other, null)) {
        return false;
      }
      if (ReferenceEquals(other, this)) {
        return true;
      }
      if (!object.Equals(AgentInfo, other.AgentInfo)) return false;
      if (!object.Equals(AgentProto, other.AgentProto)) return false;
      return Equals(_unknownFields, other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public override int GetHashCode() {
      int hash = 1;
      if (agentInfo_ != null) hash ^= AgentInfo.GetHashCode();
      if (agentProto_ != null) hash ^= AgentProto.GetHashCode();
      if (_unknownFields != null) {
        hash ^= _unknownFields.GetHashCode();
      }
      return hash;
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public override string ToString() {
      return pb::JsonFormatter.ToDiagnosticString(this);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public void WriteTo(pb::CodedOutputStream output) {
      if (agentInfo_ != null) {
        output.WriteRawTag(10);
        output.WriteMessage(AgentInfo);
      }
      if (agentProto_ != null) {
        output.WriteRawTag(18);
        output.WriteMessage(AgentProto);
      }
      if (_unknownFields != null) {
        _unknownFields.WriteTo(output);
      }
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public int CalculateSize() {
      int size = 0;
      if (agentInfo_ != null) {
        size += 1 + pb::CodedOutputStream.ComputeMessageSize(AgentInfo);
      }
      if (agentProto_ != null) {
        size += 1 + pb::CodedOutputStream.ComputeMessageSize(AgentProto);
      }
      if (_unknownFields != null) {
        size += _unknownFields.CalculateSize();
      }
      return size;
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public void MergeFrom(AgentInfoActionPairProto other) {
      if (other == null) {
        return;
      }
      if (other.agentInfo_ != null) {
        if (agentInfo_ == null) {
          agentInfo_ = new global::MLAgents.CommunicatorObjects.AgentInfoProto();
        }
        AgentInfo.MergeFrom(other.AgentInfo);
      }
      if (other.agentProto_ != null) {
        if (agentProto_ == null) {
          agentProto_ = new global::MLAgents.CommunicatorObjects.AgentActionProto();
        }
        AgentProto.MergeFrom(other.AgentProto);
      }
      _unknownFields = pb::UnknownFieldSet.MergeFrom(_unknownFields, other._unknownFields);
    }

    [global::System.Diagnostics.DebuggerNonUserCodeAttribute]
    public void MergeFrom(pb::CodedInputStream input) {
      uint tag;
      while ((tag = input.ReadTag()) != 0) {
        switch(tag) {
          default:
            _unknownFields = pb::UnknownFieldSet.MergeFieldFrom(_unknownFields, input);
            break;
          case 10: {
            if (agentInfo_ == null) {
              agentInfo_ = new global::MLAgents.CommunicatorObjects.AgentInfoProto();
            }
            input.ReadMessage(agentInfo_);
            break;
          }
          case 18: {
            if (agentProto_ == null) {
              agentProto_ = new global::MLAgents.CommunicatorObjects.AgentActionProto();
            }
            input.ReadMessage(agentProto_);
            break;
          }
        }
      }
    }

  }

  #endregion

}

#endregion Designer generated code
