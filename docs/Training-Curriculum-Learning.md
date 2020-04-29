# Training with Curriculum Learning

Curriculum learning is a feature of ML-Agents which allows for the properties of environments to be changed during the training process to aid in learning.

## An Instructional Example

*[**Note**: The example provided below is for instructional purposes, and was based on an early version of the [Wall Jump example environment](Learning-Environment-Examples.md).
As such, it is not possible to directly replicate the results here using that environment.]*

Imagine a task in which an agent needs to scale a wall to arrive at a goal. The
starting point when training an agent to accomplish this task will be a random
policy. That starting policy will have the agent running in circles, and will
likely never, or very rarely scale the wall properly to the achieve the reward.
If we start with a simpler task, such as moving toward an unobstructed goal,
then the agent can easily learn to accomplish the task. From there, we can
slowly add to the difficulty of the task by increasing the size of the wall
until the agent can complete the initially near-impossible task of scaling the
wall.

![Wall](images/curriculum.png)

_Demonstration of a hypothetical curriculum training scenario in which a progressively taller
wall obstructs the path to the goal._

## How-To

Each group of Agents under the same `Behavior Name` in an environment can have
a corresponding curriculum. These curricula are held in what we call a "metacurriculum".
A metacurriculum allows different groups of Agents to follow different curricula within
the same environment.

### Specifying Curricula

In order to define the curricula, the first step is to decide which parameters of
the environment will vary. In the case of the Wall Jump environment,
the height of the wall is what varies. We define this as a `Environment Parameters`
that can be accessed in `Academy.Instance.EnvironmentParameters`, and by doing
so it becomes adjustable via the Python API.
Rather than adjusting it by hand, we will add a section to our YAML configuration file that
describes the structure of the curricula. Within it, we can specify which
points in the training process our wall height will change, either based on the
percentage of training steps which have taken place, or what the average reward
the agent has received in the recent past is. Below is an example config for the
curricula for the Wall Jump environment. You can find the full file in `config/ppo/WallJump_curriculum.yaml`.

```yaml
behaviors:
  BigWallJump:
    trainer: ppo
    ... # The rest of the hyperparameters
    vis_encode_type: simple
    reward_signals:
      extrinsic:
        strength: 1.0
        gamma: 0.99
    curriculum: # Add this section for curriculum
      measure: progress
      thresholds: [0.1, 0.3, 0.5]
      min_lesson_length: 100
      signal_smoothing: true
      parameters:
        big_wall_min_height: [0.0, 4.0, 6.0, 8.0]
        big_wall_max_height: [4.0, 7.0, 8.0, 8.0]

  SmallWallJump:
    trainer: ppo
    ... # The rest of the hyperparameters
    reward_signals:
      extrinsic:
        strength: 1.0
        gamma: 0.99
    curriculum: # Add this section for curriculum
      measure: progress
      thresholds: [0.1, 0.3, 0.5]
      min_lesson_length: 100
      signal_smoothing: true
      parameters:
        small_wall_height: [1.5, 2.0, 2.5, 4.0]
```

For each Behavior Name described in your training configuration file, we can specify a curriculum
by adding a `curriculum:` section under that particular Behavior Name.
Note that these must be the
same as the Behavior Name in the [Agent's Behavior Parameters](Learning-Environment-Design-Agents.md#agent-properties).
The curriculum for each
behavior has the following parameters:
* `measure` - What to measure learning progress, and advancement in lessons by.
  * `reward` - Uses a measure received reward.
  * `progress` - Uses ratio of steps/max_steps.
* `thresholds` (float array) - Points in value of `measure` where lesson should
  be increased.
* `min_lesson_length` (int) - The minimum number of episodes that should be
  completed before the lesson can change. If `measure` is set to `reward`, the
  average cumulative reward of the last `min_lesson_length` episodes will be
  used to determine if the lesson should change. Must be nonnegative.

  __Important__: the average reward that is compared to the thresholds is
  different than the mean reward that is logged to the console. For example,
  if `min_lesson_length` is `100`, the lesson will increment after the average
  cumulative reward of the last `100` episodes exceeds the current threshold.
  The mean reward logged to the console is dictated by the `summary_freq`
  parameter in the
  [training configuration file](Training-ML-Agents.md#training-config-file).
* `signal_smoothing` (true/false) - Whether to weight the current progress
  measure by previous values.
  * If `true`, weighting will be 0.75 (new) 0.25 (old).
* `parameters` (dictionary of key:string, value:float array) - Corresponds to
  Environment parameters to control. Length of each array should be one
  greater than number of thresholds.

Once our curriculum is defined, we have to use the environment parameters we defined
and modify the environment from the Agent's `OnEpisodeBegin()` function. See
[WallJumpAgent.cs](https://github.com/Unity-Technologies/ml-agents/blob/master/Project/Assets/ML-Agents/Examples/WallJump/Scripts/WallJumpAgent.cs)
for an example.


### Training with a Curriculum

Once we have specified our metacurriculum and curricula, we can launch
`mlagents-learn` using the `–curriculum` flag to point to the config file
for our curricula and PPO will train using Curriculum Learning. For example,
to train agents in the Wall Jump environment with curriculum learning, you can run:

```sh
mlagents-learn config/ppo/WallJump_curriculum.yaml --run-id=wall-jump-curriculum
```

You can then keep track of the current lessons and progresses via TensorBoard.

__Note__: If you are resuming a training session that uses curriculum, please pass the number of the last-reached lesson using the `--lesson` flag when running `mlagents-learn`.
