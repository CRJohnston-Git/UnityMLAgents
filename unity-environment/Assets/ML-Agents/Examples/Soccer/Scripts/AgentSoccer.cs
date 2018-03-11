﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AgentSoccer : Agent
{

    public enum Team
    {
        red, blue
    }
    public enum AgentRole
    {
        striker, goalie
    }
    public Team team;
    public AgentRole agentRole;
    float kickPower;
    int playerIndex;
    public SoccerFieldArea area;
    [HideInInspector]
    public Rigidbody agentRB;
    SoccerAcademy academy;
    Renderer soccerRenderer;

    public void ChooseRandomTeam()
    {
        team = (Team)Random.Range(0, 2);
        soccerRenderer.material = team == Team.red ? academy.redMaterial : academy.blueMaterial;
    }

    public void JoinRedTeam(AgentRole role)
    {
        agentRole = role;
        team = Team.red;
        soccerRenderer.material = academy.redMaterial;
    }

    public void JoinBlueTeam(AgentRole role)
    {
        agentRole = role;
        team = Team.blue;
        soccerRenderer.material = academy.blueMaterial;
    }

    void Awake()
    {
        soccerRenderer = GetComponent<Renderer>();
        academy = FindObjectOfType<SoccerAcademy>();
        PlayerState playerState = new PlayerState();
        playerState.agentRB = GetComponent<Rigidbody>();
        agentRB = GetComponent<Rigidbody>();
        agentRB.maxAngularVelocity = 500;
        playerState.startingPos = transform.position;
        playerState.agentScript = this;
        area.playerStates.Add(playerState);
        playerIndex = area.playerStates.IndexOf(playerState);
        playerState.playerIndex = playerIndex;
    }

    public override void InitializeAgent()
    {
        base.InitializeAgent();
    }

    public void RayPerception(float rayDistance,
                             float[] rayAngles, string[] detectableObjects,
                              float startHeight, float endHeight)
    {
        foreach (float angle in rayAngles)
        {
            float noise = 0f;
            float noisyAngle = angle + Random.Range(-noise, noise);
            Vector3 position = transform.TransformDirection(
                GiveCatersian(rayDistance, noisyAngle));
            position.y = endHeight;
            Debug.DrawRay(transform.position + new Vector3(0f, startHeight, 0f),
                          position, Color.red, 0.1f, true);
            RaycastHit hit;
            float[] subList = new float[detectableObjects.Length + 2];
            if (Physics.SphereCast(transform.position +
                                   new Vector3(0f, startHeight, 0f), 1.0f,
                                   position, out hit, rayDistance))
            {
                for (int i = 0; i < detectableObjects.Length; i++)
                {
                    if (hit.collider.gameObject.CompareTag(detectableObjects[i]))
                    {
                        subList[i] = 1;
                        subList[detectableObjects.Length + 1] = hit.distance / rayDistance;
                        break;
                    }
                }
            }
            else
            {
                subList[detectableObjects.Length] = 1f;
            }
            foreach (float f in subList)
                AddVectorObs(f);
        }
    }

    public Vector3 GiveCatersian(float radius, float angle)
    {
        float x = radius * Mathf.Cos(DegreeToRadian(angle));
        float z = radius * Mathf.Sin(DegreeToRadian(angle));
        return new Vector3(x, 1f, z);
    }

    public float DegreeToRadian(float degree)
    {
        return degree * Mathf.PI / 180f;
    }

    public override void CollectObservations()
    {
        float rayDistance = 20f;
        float[] rayAngles = { 0f, 45f, 90f, 135f, 180f, 110f, 70f };
        string[] detectableObjects;
        if (team == Team.red)
        {
            detectableObjects = new string[] { "ball", "redGoal", "blueGoal",
                "wall", "redAgent", "blueAgent" };
        }
        else
        {
            detectableObjects = new string[] { "ball", "blueGoal", "redGoal",
                "wall", "blueAgent", "redAgent" };
        }
        RayPerception(rayDistance, rayAngles, detectableObjects, 0f, 0f);
        RayPerception(rayDistance, rayAngles, detectableObjects, 1f, 1f);
    }

    public void MoveAgent(float[] act)
    {
        Vector3 dirToGo = Vector3.zero;
        Vector3 rotateDir = Vector3.zero;

        int action = Mathf.FloorToInt(act[0]);

        // Goalies and Strikers have slightly different action spaces.
        if (agentRole == AgentRole.goalie)
        {
            kickPower = 0f;
            if (action == 0)
            {
                dirToGo = transform.forward * 1f;
                kickPower = 1f;
            }
            else if (action == 1)
            {
                dirToGo = transform.forward * -1f;
            }
            else if (action == 3)
            {
                dirToGo = transform.right * -1f;
            }
            else if (action == 2)
            {
                dirToGo = transform.right * 1f;
            }

        }
        else
        {
            kickPower = 0f;
            if (action == 0)
            {
                dirToGo = transform.forward * 1f;
                kickPower = 1f;
            }
            else if (action == 1)
            {
                dirToGo = transform.forward * -1f;
            }
            else if (action == 2)
            {
                rotateDir = transform.up * 1f;
            }
            else if (action == 3)
            {
                rotateDir = transform.up * -1f;
            }
            else if (action == 4)
            {
                dirToGo = transform.right * -1f;
            }
            else if (action == 5)
            {
                dirToGo = transform.right * 1f;
            }
        }
        transform.Rotate(rotateDir, Time.deltaTime * 100f);
        agentRB.AddForce(dirToGo * academy.agentRunSpeed,
                         ForceMode.VelocityChange);

    }


    public override void AgentAction(float[] vectorAction, string textAction)
    {
        // Existential penalty for strikers.
        if (agentRole == AgentRole.striker)
        {
            AddReward(-1f / 3000f);
        }
        // Existential bonus for goalies.
        if (agentRole == AgentRole.goalie)
        {
            AddReward(1f / 3000f);
        }
        MoveAgent(vectorAction);

    }

    /// <summary>
    /// Used to provide a "kick" to the ball.
    /// </summary>
    void OnCollisionEnter(Collision c)
    {
        float force = 2000f * kickPower;
        if (c.gameObject.tag == "ball")
        {
            Vector3 dir = c.contacts[0].point - transform.position;
            dir = dir.normalized;
            c.gameObject.GetComponent<Rigidbody>().AddForce(dir * force);
        }
    }


    public override void AgentReset()
    {
        if (academy.randomizePlayersTeamForTraining)
        {
            ChooseRandomTeam();
        }

        if (team == Team.red)
        {
            JoinRedTeam(agentRole);
            transform.rotation = Quaternion.Euler(0f, -90f, 0f);
        }
        else
        {
            JoinBlueTeam(agentRole);
            transform.rotation = Quaternion.Euler(0f, 90f, 0f);
        }
        transform.position = area.GetRandomSpawnPos(team.ToString(),
                                                    agentRole.ToString());
        agentRB.velocity = Vector3.zero;
        agentRB.angularVelocity = Vector3.zero;
        area.ResetBall();
    }

    public override void AgentOnDone()
    {

    }
}
