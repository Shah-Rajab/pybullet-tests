################# DOES'T WORK

import gym

from baselines.common.vec_env import DummyVecEnv
from baselines.ppo2 import Model


# Optional: PPO2 requires a vectorized environment to run
# the env is now wrapped automatically when passing it to the constructor
# env = DummyVecEnv([lambda: env])


if __name__ == '__main__':
    env = gym.make('walk-forward-v0')
    model = Model('mlp', env, verbose=1)
    model.learn(total_timesteps=10000)

    obs = env.reset()
    for i in range(1000):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        env.render()

    observation = env.reset()
    for t in range(1000):
        env.render()
        print(observation)
        action = env.action_space.sample()
        observation, reward, done, info = env.step(env.action_space.sample())  # take a random action
        if done:
            print("Episode finished after {} timesteps".format(t + 1))
            break
    env.close()
    #print(tf.test.gpu_device_name())
    #tf.test.is_gpu_available(
    #    cuda_only=False, min_cuda_compute_capability=None
    #)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
