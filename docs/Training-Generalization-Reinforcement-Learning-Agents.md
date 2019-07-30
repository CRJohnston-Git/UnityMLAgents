# Training Generalized Reinforcement Learning Agents

Reinforcement learning has a rather unique setup as opposed to supervised and
unsupervised learning. Agents here are trained and tested on the same exact 
environment, which is analogous to a model being trained and tested on an 
identical dataset in supervised learning! This setting results in overfitting; 
the inability of the agent to generalize to slight tweaks or variations in the 
environment. This is problematic in instances when environments are randomly 
instantiated with varying properties. To make agents robust, one approach is to
train an agent over multiple variations of the environment. The agent is 
trained in this approach with the intent that it learns to adapt its performance 
to future unseen variations of the environment.

Ball scale of 0.5          |  Ball scale of 4
:-------------------------:|:-------------------------:
![](images/3dball_small.png)  |  ![](images/3dball_big.png)

_Variations of the 3D Ball environment._

To vary environments, we first decide what parameters to vary in an
environment. We call these parameters `Reset Parameters`. In the 3D ball 
environment example displayed in the figure above, the reset parameters are 
`gravity`, `ball_mass` and `ball_scale`.


## How-to

For generalization training, we need to provide a way to modify the environment 
by supplying a set of reset parameters, and vary them over time. This provision
can be done either deterministically or randomly. 

This is done by assigning each reset parameter a sampler, which samples a reset
parameter value (such as a uniform sampler). If a sampler isn't provided for a
reset parameter, the parameter maintains the default value throughout the 
training procedure, remaining unchanged. The samplers for all the reset parameters 
are handled by a **Sampler Manager**, which also handles the generation of new 
values for the reset parameters when needed. 

To setup the Sampler Manager, we setup a YAML file that specifies how we wish to 
generate new samples. In this file, we specify the samplers and the 
`resampling-interval` (number of simulation steps after which reset parameters are 
resampled). Below is an example of a sampler file for the 3D ball environment.

```yaml
resampling-interval: 5000

mass:
    sampler-type: "uniform"
    min_value: 0.5
    max_value: 10

gravity:
    sampler-type: "multirange_uniform"
    intervals: [[7, 10], [15, 20]]

scale:
    sampler-type: "uniform"
    min_value: 0.75
    max_value: 3

```

* `resampling-interval` (int) - Specifies the number of steps for agent to 
train under a particular environment configuration before resetting the 
environment with a new sample of reset parameters.

* `parameter_name` - Name of the reset parameter. This should match the name 
specified in the academy of the intended environment for which the agent is 
being trained. If a parameter specified in the file doesn't exist in the 
environment, then this specification will be ignored.

    * `sampler-type` - Specify the sampler type to use for the reset parameter. 
    This is a string that should exist in the `Sampler Factory` (explained 
    below).

    * `sub-arguments` - Specify the characteristic parameters for the sampler. 
    In the example sampler file above, this would correspond to the `intervals` 
    key under the `multirange_uniform` sampler for the gravity reset parameter. 
    The key name should match the name of the corresponding argument in the sampler definition. (Look at defining a new sampler method)


The sampler manager allocates a sampler for a reset parameter by using the *Sampler Factory*, which maintains a dictionary mapping of string keys to sampler objects. The available samplers to be used for reset parameter resampling is as available in the Sampler Factory.

#### Possible Sampler Types

The currently implemented samplers that can be used with the `sampler-type` arguments are:

* `uniform` - Uniform sampler
    *   Uniformly samples a single float value between defined endpoints. 
        The sub-arguments for this sampler to specify the interval 
        endpoints are as below. The sampling is done in the range of 
        [`min_value`, `max_value`).

    * **sub-arguments** - `min_value`, `max_value`

* `gaussian` - Gaussian sampler 
    *   Samples a single float value from the distribution characterized by
        the mean and standard deviation. The sub-arguments to specify the 
        gaussian distribution to use are as below.

    * **sub-arguments** - `mean`, `st_dev`

* `multirange_uniform` - Multirange Uniform sampler
    *   Uniformly samples a single float value between the specified intervals. 
        Samples by first performing a weight pick of an interval from the list 
        of intervals (weighted based on interval width) and samples uniformly 
        from the selected interval (half-closed interval, same as the uniform 
        sampler). This sampler can take an arbitrary number of intervals in a 
        list in the following format: 
    [[`interval_1_min`, `interval_1_max`], [`interval_2_min`, `interval_2_max`], ...]
    
    * **sub-arguments** - `intervals`


The implementation of the samplers can be found at `ml-agents-envs/mlagents/envs/sampler_class.py`.

### Defining a new sampler method

Custom sampling techniques must inherit from the *Sampler* base class (included in the `sampler_class` file) and preserve the interface. Once the class for the required method is specified, it must be registered in the Sampler Factory. 

This can be done by subscribing to the *register_sampler* method of the SamplerFactory. The command is as follows:

`SamplerFactory.register_sampler(*custom_sampler_string_key*, *custom_sampler_object*)`

Once the Sampler Factory reflects the new register, the custom sampler can be used for resampling reset parameter. For demonstration, lets say our sampler was implemented as below, and we register the `CustomSampler` class with the string `custom-sampler` in the Sampler Factory.

```python
class CustomSampler(Sampler):

    def __init__(self, argA, argB, argC):
        self.possible_vals = [argA, argB, argC]

    def sample_all(self):
        return np.random.choice(self.possible_vals)
```

Now we need to specify this sampler in the sampler file. Lets say we wish to use this sampler for the reset parameter *mass*; the sampler file would specify the same for mass as the following (any order of the subarguments is valid).

```yaml
mass:
    sampler-type: "custom-sampler"
    argB: 1
    argA: 2
    argC: 3
```

With the sampler file setup, we can proceed to train our agent as explained in the next section.

### Training with Generalization Learning

We first begin with setting up the sampler file. After the sampler file is defined and configured, we proceed by launching `mlagents-learn` and specify our configured sampler file with the `--sampler` flag. To demonstrate, if we wanted to train a 3D ball agent with generalization using the `config/3dball_generalize.yaml` sampling setup, we can run

```sh
mlagents-learn config/trainer_config.yaml --sampler=config/3dball_generalize.yaml --run-id=3D-Ball-generalization --train
```

We can observe progress and metrics via Tensorboard.
