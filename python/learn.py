# # Unity ML Agents
# ## ML-Agent Learning (PPO)
# Launches trainers for each External Brains in a Unity Environemnt

import logging
import os
import re
import yaml

from docopt import docopt

from trainers.ghost_trainer import GhostTrainer
from trainers.ppo_models import *
from trainers.ppo_trainer import PPOTrainer
from unityagents import UnityEnvironment, UnityEnvironmentException

def get_progress():
    if curriculum_file is not None:
        if env.curriculum.measure_type == "progress":
            progress = 0
            for brain_name in env.external_brain_names:
                progress += trainers[brain_name].get_step / trainers[brain_name].get_max_steps
            return progress / len(env.external_brain_names)
        elif env.curriculum.measure_type == "reward":
            progress = 0
            for brain_name in env.external_brain_names:
                progress += trainers[brain_name].get_last_reward 
            return progress
        else:
            return None
    else:
        return None

if __name__ == '__main__' :
    logger = logging.getLogger("unityagents")
    _USAGE = '''
    Usage:
      ppo (<env>) [options] 

    Options:
      --help                     Show this message.
      --batch-size=<n>           How many experiences per gradient descent update step [default: 64].
      --beta=<n>                 Strength of entropy regularization [default: 2.5e-3].
      --buffer-size=<n>          How large the experience buffer should be before gradient descent [default: 2048].
      --curriculum=<file>        Curriculum json file for environment [default: None].
      --epsilon=<n>              Acceptable threshold around ratio of old and new policy probabilities [default: 0.2].
      --gamma=<n>                Reward discount rate [default: 0.99].
      --hidden-units=<n>         Number of units in hidden layer [default: 64].
      --keep-checkpoints=<n>     How many model checkpoints to keep [default: 5].
      --lambd=<n>                Lambda parameter for GAE [default: 0.95].
      --learning-rate=<rate>     Model learning rate [default: 3e-4].
      --lesson=<n>               Start learning from this lesson [default: 0].
      --load                     Whether to load the model or randomly initialize [default: False].
      --max-steps=<n>            Maximum number of steps to run environment [default: 1e6].
      --normalize                Whether to normalize the state input using running statistics [default: False].
      --num-epoch=<n>            Number of gradient descent steps per batch of experiences [default: 5].
      --num-layers=<n>           Number of hidden layers between state/observation and outputs [default: 2].
      --run-path=<path>          The sub-directory name for model and summary statistics [default: ppo].
      --save-freq=<n>            Frequency at which to save model [default: 50000].
      --sequence-length=<n>      The training length of states used for recurrent state encoding [default: 32]. 
      --summary-freq=<n>         Frequency at which to save training statistics [default: 10000].
      --time-horizon=<n>         How many steps to collect per agent before adding to buffer [default: 2048].
      --train                    Whether to train model, or only run inference [default: False].
      --use-recurrent            Whether to use recurrent encoding of the state and observations [default: False].
      --worker-id=<n>            Number to add to communication port (5005). Used for multi-environment [default: 0].
    '''

    options = docopt(_USAGE)
    logger.info(options)

    # General parameters
    model_path = './models/{}'.format(str(options['--run-path']))

    # summary_path = './summaries/{}'.format(str(options['--run-path']))
    load_model = options['--load']
    train_model = options['--train']
    save_freq = int(options['--save-freq'])
    env_name = options['<env>']
    keep_checkpoints = int(options['--keep-checkpoints'])
    worker_id = int(options['--worker-id'])
    curriculum_file = str(options['--curriculum'])
    if curriculum_file == "None":
        curriculum_file = None
    lesson = int(options['--lesson'])

    default_trainer_parameters = {
        'max_steps':float(options['--max-steps']), 
        'gamma':float(options['--gamma']),
        'lambd':float(options['--lambd']), 
        'time_horizon':int(options['--time-horizon']),
        'beta':float(options['--beta']), 
        'num_epoch':int(options['--num-epoch']), 
        'epsilon':float(options['--epsilon']), 
        'buffer_size':int(options['--buffer-size']),
        'learning_rate':float(options['--learning-rate']), 
        'hidden_units':int(options['--hidden-units']), 
        'batch_size':int(options['--batch-size']),
        'normalize':options['--normalize'], 
        'summary_freq':int(options['--summary-freq']), 
        'num_layers':int(options['--num-layers']),
        'use_recurrent':options['--use-recurrent'],
        'sequence_length':int(options['--sequence-length'])
        }

    env = UnityEnvironment(file_name=env_name, worker_id=worker_id, curriculum=curriculum_file)
    env.curriculum.set_lesson_number(lesson)
    logger.info(str(env))

    tf.reset_default_graph()

    try:
        if not os.path.exists(model_path):
            os.makedirs(model_path)
    except:
        raise UnityEnvironmentException("The folder {} containing the generated model could not be accessed."
          " Please make sure the permissions are set correctly.".format(model_path))

    try:
        with open("trainer_configurations.yaml") as data_file:
            trainer_configurations = yaml.load(data_file)
    except IOError:
        logger.info("The file {0} could not be found. Will use default Hyperparameters".format("trainer_configurations.yaml"))
        trainer_configurations = {}
    except UnicodeDecodeError:
        raise UnityEnvironmentException("There was an error decoding {}".format("trainer_configurations.json"))

    with tf.Session() as sess:
        trainers = {}
        trainer_parameters_dict = {}
        for brain_name in env.external_brain_names:
            trainer_parameters = default_trainer_parameters.copy()
            if len(env.external_brain_names) > 1:
                graph_scope = re.sub('[^0-9a-zA-Z]+', '-', brain_name)
                trainer_parameters['graph_scope'] = graph_scope
                trainer_parameters['summary_path'] = './summaries/{}'.format(str(options['--run-path']))+'__'+graph_scope
            else :
                trainer_parameters['graph_scope'] = ''
                trainer_parameters['summary_path'] = './summaries/{}'.format(str(options['--run-path']))
            if brain_name in trainer_configurations:
                _brain_key = brain_name
                while not isinstance(trainer_configurations[_brain_key], dict):
                    _brain_key = trainer_configurations[_brain_key]
                for k in trainer_configurations[_brain_key]:
                    trainer_parameters[k] = trainer_configurations[_brain_key][k]
            logger.info("Hyperparameters for {}:".format(brain_name))
            logger.info(trainer_parameters)
            trainer_parameters_dict[brain_name] = trainer_parameters.copy()
        for brain_name in env.external_brain_names:
            if 'is_ghost' not in trainer_parameters_dict[brain_name]:
                trainer_parameters_dict[brain_name]['is_ghost'] = False
            if trainer_parameters_dict[brain_name]['is_ghost']:
                trainer_parameters_dict[brain_name]['original_brain_parameters'] = trainer_parameters_dict[
                    trainer_parameters_dict[brain_name]['brain_to_copy']]
                trainers[brain_name] = GhostTrainer(sess, env, brain_name, trainer_parameters_dict[brain_name], train_model)
            else:
                trainers[brain_name] = PPOTrainer(sess, env, brain_name, trainer_parameters_dict[brain_name], train_model)
        init = tf.global_variables_initializer()
        saver = tf.train.Saver(max_to_keep=keep_checkpoints)
        # Instantiate model parameters
        if load_model:
            logger.info('Loading Model...')
            ckpt = tf.train.get_checkpoint_state(model_path)
            if ckpt == None:
              logger.info('The model {0} could not be found. Make sure you specified the right '
                '--run-path'.format(model_path))
            saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            sess.run(init)
        global_step = 0 # This is only for saving the model
        env.curriculum.increment_lesson(get_progress())
        info = env.reset(train_mode=train_model)
        if train_model:
            for brain_name, trainer in trainers.items():
                trainer.write_tensorboard_text('Hyperparameters', trainer.parameters) 
        try:
            while any([t.get_step < t.get_max_steps for k, t in trainers.items()]) or not train_model:
                if env.global_done:
                    env.curriculum.increment_lesson(get_progress())
                    info = env.reset(train_mode=train_model)
                    for brain_name, trainer in trainers.items():
                        trainer.end_episode()
                # Decide and take an action
                take_action_actions = {}
                take_action_memories = {}
                take_action_values = {}
                take_action_outputs = {}
                for brain_name, trainer in trainers.items():
                    (take_action_actions[brain_name],
                    take_action_memories[brain_name],
                    take_action_values[brain_name], 
                    take_action_outputs[brain_name]) = trainer.take_action(info)
                new_info = env.step(action = take_action_actions, memory = take_action_memories, value = take_action_values)
                for brain_name, trainer in trainers.items():
                    trainer.add_experiences(info, new_info, take_action_outputs[brain_name])
                info = new_info
                for brain_name, trainer in trainers.items():
                    trainer.process_experiences(info)
                    if trainer.is_ready_update() and train_model:
                        # Perform gradient descent with experience buffer
                        trainer.update_model()
                    # Write training statistics to tensorboard.
                    trainer.write_summary(env.curriculum.lesson_number)
                    if train_model:
                        trainer.increment_step()
                        trainer.update_last_reward()
                if train_model:
                    global_step += 1
                if global_step % save_freq == 0 and global_step != 0 and train_model:
                    # Save Tensorflow model
                    save_model(sess, model_path=model_path, steps=global_step, saver=saver)

            # Final save Tensorflow model
            if global_step != 0 and train_model:
                save_model(sess, model_path=model_path, steps=global_step, saver=saver)
        except KeyboardInterrupt:
          logger.info("Learning was interupted. Please wait while the graph is generated.")
          save_model(sess, model_path=model_path, steps=global_step, saver=saver)
          pass
    env.close()
    graph_name = (env_name.strip()
          .replace('.app', '').replace('.exe', '').replace('.x86_64', '').replace('.x86', ''))
    graph_name = os.path.basename(os.path.normpath(graph_name))
    nodes = []
    scopes = []
    for brain_name in trainers.keys():
        if trainers[brain_name].graph_scope is not None:
            scope = trainers[brain_name].graph_scope + '/'
            if scope == '/':
              scope = ''
            scopes += [scope]
            if not trainers[brain_name].parameters["use_recurrent"]:
                nodes +=[scope + x for x in ["action","value_estimate","action_probs"]] 
            else:
                nodes +=[scope + x for x in ["action","value_estimate","action_probs","recurrent_out"]] 
    export_graph(model_path, graph_name, target_nodes=','.join(nodes))
    if len(scopes) > 1:
        logger.info("List of available scopes :")
        for scope in scopes:
            logger.info("\t" + scope )
    logger.info("List of nodes exported :")
    for n in nodes:
        logger.info("\t" + n)  

