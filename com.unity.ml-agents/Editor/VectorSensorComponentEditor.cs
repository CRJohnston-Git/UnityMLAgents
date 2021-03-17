using UnityEditor;
using Unity.MLAgents.Sensors;

namespace Unity.MLAgents.Editor
{
    [CustomEditor(typeof(VectorSensorComponent))]
    [CanEditMultipleObjects]
    internal class VectorSensorComponentEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            var so = serializedObject;
            so.Update();

            // Drawing the VectorSensorComponent
            EditorGUI.BeginChangeCheck();

            EditorGUI.BeginDisabledGroup(!EditorUtilities.CanUpdateModelProperties());
            {
                // These fields affect the sensor order or observation size,
                // So can't be changed at runtime.
                EditorGUILayout.PropertyField(so.FindProperty("m_observationSize"), true);
                EditorGUILayout.PropertyField(so.FindProperty("m_ObservationType"), true);
            }
            EditorGUI.EndDisabledGroup();

            var requireSensorUpdate = EditorGUI.EndChangeCheck();
            so.ApplyModifiedProperties();

            if (requireSensorUpdate)
            {
                UpdateSensor();
            }
        }

        void UpdateSensor()
        {
            var sensorComponent = serializedObject.targetObject as VectorSensorComponent;
            sensorComponent?.UpdateSensor();
        }
    }
}
