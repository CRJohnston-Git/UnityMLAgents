# Example Learning Environments

Unity ML-Agents contains an expanding set of example environments which
demonstrate various features of the platform. Environments are located in 
`unity-environment/Assets/ML-Agents/Examples` and summarised below. 
Additionally, our 
[first ML Challenge](https://connect.unity.com/challenges/ml-agents-1)
contains environments created by the community.

This page only overviews the example environments we provide. To learn more
on how to design and build your own environments see our 
[Making a new Learning Environment](Learning-Environment-Create-New.md)
page.

If you would like to contribute environments, please see our 
[contribution guidelines](Contribution-Guidelines.md) page. 

## Basic

![Basic](images/basic.png)

* Set-up: A linear movement task where the agent must move left or right to rewarding states.
* Goal: Move to the most reward state.
* Agents: The environment contains one agent linked to a single brain.
* Agent Reward Function: 
    * +0.1 for arriving at suboptimal state.
    * +1.0 for arriving at optimal state.
* Brains: One brain with the following observation/action space.
    * State space: (Discrete) One variable corresponding to current state.
    * Action space: (Discrete) Two possible actions (Move left, move right).
    * Visual Observations: 0
* Reset Parameters: None

## 3DBall

![Balance Ball](images/balance.png)

* Set-up: A balance-ball task, where the agent controls the platform. 
* Goal: The agent must balance the platform in order to keep the ball on it for as long as possible.
* Agents: The environment contains 12 agents of the same kind, all linked to a single brain.
* Agent Reward Function: 
    * +0.1 for every step the ball remains on the platform. 
    * -1.0 if the ball falls from the platform.
* Brains: One brain with the following observation/action space.
    * Vector Observation space: (Continuous) 8 variables corresponding to rotation of platform, and position, rotation, and velocity of ball.
    * Vector Observation space (Hard Version): (Continuous) 5 variables corresponding to rotation of platform and position and rotation of ball.
    * Action space: (Continuous) Size of 2, with one value corresponding to X-rotation, and the other to Z-rotation.
    * Visual Observations: 0
* Reset Parameters: None

## GridWorld

![GridWorld](images/gridworld.png)

* Set-up: A version of the classic grid-world task. Scene contains agent, goal, and obstacles. 
* Goal: The agent must navigate the grid to the goal while avoiding the obstacles.
* Agents: The environment contains one agent linked to a single brain.
* Agent Reward Function: 
    * -0.01 for every step.
    * +1.0 if the agent navigates to the goal position of the grid (episode ends).
    * -1.0 if the agent navigates to an obstacle (episode ends).
* Brains: One brain with the following observation/action space.
    * Vector Observation space: None
    * Action space: (Discrete) Size of 4, corresponding to movement in cardinal directions.
    * Visual Observations: One corresponding to top-down view of GridWorld.
* Reset Parameters: Three, corresponding to grid size, number of obstacles, and number of goals.


## Tennis

![Tennis](images/tennis.png)

* Set-up: Two-player game where agents control rackets to bounce ball over a net. 
* Goal: The agents must bounce ball between one another while not dropping or sending ball out of bounds.
* Agents: The environment contains two agent linked to a single brain.
* Agent Reward Function (independent): 
    * +0.1 To agent when hitting ball over net.
    * -0.1 To agent who let ball hit their ground, or hit ball out of bounds.
* Brains: One brain with the following observation/action space.
    * Vector Observation space: (Continuous) 8 variables corresponding to position and velocity of ball and racket.
    * Action space: (Continuous) Size of 2, corresponding to movement toward net or away from net, and jumping.
    * Visual Observations: None
* Reset Parameters: One, corresponding to size of ball.

## Area 

### Push Area

![Push](images/push.png)

* Set-up: A platforming environment where the agent can push a block around.
* Goal: The agent must push the block to the goal.
* Agents: The environment contains one agent linked to a single brain.
* Agent Reward Function: 
    * -0.01 for every step.
    * +1.0 if the block touches the goal.
    * -1.0 if the agent falls off the platform.
* Brains: One brain with the following observation/action space.
    * Vector Observation space: (Continuous) 15 variables corresponding to position and velocities of agent, block, and goal.
    * Action space: (Discrete) Size of 6, corresponding to movement in cardinal directions, jumping, and no movement.
    * Visual Observations: None.
* Reset Parameters: One, corresponding to number of steps in training. Used to adjust size of elements for Curriculum Learning.

### Wall Area

![Wall](images/wall.png)

* Set-up: A platforming environment where the agent can jump over a wall.
* Goal: The agent must use the block to scale the wall and reach the goal.
* Agents: The environment contains one agent linked to a single brain.
* Agent Reward Function: 
    * -0.01 for every step.
    * +1.0 if the agent touches the goal.
    * -1.0 if the agent falls off the platform.
* Brains: One brain with the following observation/action space.
    * Vector Observation space: (Continuous) 16 variables corresponding to position and velocities of agent, block, and goal, plus the height of the wall.
    * Action space: (Discrete) Size of 6, corresponding to movement in cardinal directions, jumping, and no movement.
    * Visual Observations: None.
* Reset Parameters: One, corresponding to number of steps in training. Used to adjust size of the wall for Curriculum Learning.

## Reacher

![Tennis](images/reacher.png)

* Set-up: Double-jointed arm which can move to target locations.
* Goal: The agents must move it's hand to the goal location, and keep it there.
* Agents: The environment contains 32 agent linked to a single brain.
* Agent Reward Function (independent): 
    * +0.1 Each step agent's hand is in goal location.
* Brains: One brain with the following observation/action space.
    * Vector Observation space: (Continuous) 26 variables corresponding to position, rotation, velocity, and angular velocities of the two arm rigidbodies.
    * Action space: (Continuous) Size of 4, corresponding to torque applicable to two joints. 
    * Visual Observations: None
* Reset Parameters: Two, corresponding to goal size, and goal movement speed.

## Crawler

![Crawler](images/crawler.png)

* Set-up: A creature with 4 arms and 4 forearms.
* Goal: The agents must move its body along the x axis without falling.
* Agents: The environment contains 3 agent linked to a single brain.
* Agent Reward Function (independent): 
    * +1 times velocity in the x direction
    * -1 for falling.
    * -0.01 times the action squared
    * -0.05 times y position change
    * -0.05 times velocity in the z direction 
* Brains: One brain with the following observation/action space.
    * Vector Observation space: (Continuous) 117 variables corresponding to position, rotation, velocity, and angular velocities of each limb plus the acceleration and angular acceleration of the body.
    * Action space: (Continuous) Size of 12, corresponding to torque applicable to 12 joints. 
    * Visual Observations: None
* Reset Parameters: None

## Banana Collector

![Banana](images/banana.png)

* Set-up: A multi-agent environment where agents compete to collect bananas. 
* Goal: The agents must learn to move to as many yellow bananas as possible while avoiding red bananas.
* Agents: The environment contains 10 agents linked to a single brain.
* Agent Reward Function (independent): 
    * +1 for interaction with yellow banana
    * -1 for interaction with red banana.
* Brains: One brain with the following observation/action space.
    * Vector Observation space: (Continuous) 51 corresponding to velocity of agent, plus ray-based perception of objects around agent's forward direction.
    * Action space: (Continuous) Size of 3, corresponding to forward movement, y-axis rotation, and whether to use laser to disable other agents.
    * Visual Observations (Optional): First-person view for each agent. 
* Reset Parameters: None

## Hallway

![Hallway](images/hallway.png)

* Set-up: Environment where the agent needs to find information in a room, remeber it, and use it to move to the correct goal.
* Goal: Move to the goal which corresponds to the color of the block in the room.
* Agents: The environment contains one agent linked to a single brain.
* Agent Reward Function (independent):
    * +1 For moving to correct goal.
    * -0.1 For moving to incorrect goal.
    * -0.0003 Existential penalty.
* Brains: One brain with the following observation/action space:
    * Vector Observation space: (Continuous) 30 corresponding to local ray-casts detecting objects, goals, and walls.
    * Action space: (Discrete) 4 corresponding to agent rotation and forward/backward movement.
    * Visual Observations (Optional): First-person view for the agent.
* Reset Parameters: None
