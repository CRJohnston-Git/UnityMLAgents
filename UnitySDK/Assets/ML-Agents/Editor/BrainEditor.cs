﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using UnityEditor;
using System.Linq;

namespace MLAgents
{
    /// <summary>
    /// CustomEditor for the Brain base class. Defines the default Inspector view for a Brain.
    /// Shows the BrainParameters of the Brain and expose a tool to deep copy BrainParameters
    /// between brains.
    /// </summary>
    [CustomEditor(typeof(Brain))]
    public class BrainEditor : Editor
    {        
        public override void OnInspectorGUI()
        {
            var brain = (Brain) target;
            var brainToCopy = EditorGUILayout.ObjectField(
                "Copy Brain Parameters from : ", null, typeof(Brain), false) as Brain;
            if (brainToCopy != null)
            {
                brain.brainParameters = brainToCopy.brainParameters.Clone();
            }
            var serializedBrain = serializedObject;
            serializedBrain.Update(); 
            EditorGUILayout.PropertyField(serializedBrain.FindProperty("brainParameters"), true);
            serializedBrain.ApplyModifiedProperties();
            
            // Draws a horizontal thick line
            EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
        }
    }
}