using Grpc.Core;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
#if UNITY_EDITOR
using UnityEditor;
#endif
using UnityEngine;

namespace MLAgents.Communicator
{
    /// Responsible for communication with Python API.
    public class RpcCommunicator2 : Communicator
    {

        UnityToPython.UnityToPythonClient client;

        CommunicatorParameters communicatorParameters;

        public RpcCommunicator2(CommunicatorParameters communicatorParameters)
        {
            this.communicatorParameters = communicatorParameters;

        }

        public PythonParameters Initialize(AcademyParameters academyParameters,
                                           out UnityRLInput unityInput)
        {
            
            Channel channel = new Channel("localhost:"+communicatorParameters.Port, ChannelCredentials.Insecure);

            client = new UnityToPython.UnityToPythonClient(channel);
            UnityInitializationOutput initOutput = new UnityInitializationOutput();
            initOutput.Header = new Header { Status = 200 };
            initOutput.AcademyParameters = academyParameters;
            var result = client.Initialize(initOutput).PythonParameters;
            UnityOutput output = new UnityOutput();
            output.Header = new Header { Status = 200 };
            unityInput = client.Send(output).RlInput;
#if UNITY_EDITOR
            EditorApplication.playModeStateChanged += HandleOnPlayModeChanged;
#endif
            return result;
        }

        public void Close()
        {
            try
            {
                UnityOutput output = new UnityOutput();
                output.Header = new Header { Status = 400 };
                client.Send(output);
            }
            catch
            {
                return;
            }
        }

        public UnityRLInput SendOuput(UnityRLOutput unityOutput)
        {
            UnityOutput output = new UnityOutput();
            output.Header = new Header { Status = 200 };
            output.RlOutput = unityOutput;
            try
            {
                return client.Send(output).RlInput;
            }
            catch
            {
                return null;
            }
        }

#if UNITY_EDITOR
        /// Ends connection and closes environment
        private void OnApplicationQuit()
        {
            Close();
        }

        void HandleOnPlayModeChanged(PlayModeStateChange state)
        {
            // This method is run whenever the playmode state is changed.
            if (state==PlayModeStateChange.ExitingPlayMode)
            {
                Close();
            }
        }
#endif

    }
}
