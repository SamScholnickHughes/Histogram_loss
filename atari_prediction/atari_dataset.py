"""Class for atari prediction RL datasets."""

import tensorflow as tf
from experiment.dataset import Dataset
import numpy as np
import os
import gym


class RLDataset(Dataset):
    """A dataset containing observations and returns for an RL agent from an atari game.
    
    Params:
        action_file - path to file containing the agent's actions
        returns_file - path to file containing the precomputed returns
        game - the name of the game
        kwargs - dataset superclass arguments (batch_size, buffer_size, prefetch)

    NOTE: This dataset returns a function that alternates between returning training and testing generators.
        For correct results, always alternate between training and testing iterations.
    """

    def __init__(self, action_file, returns_file, game=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.returns = self.get_returns(returns_file)
        self.file = open(action_file, "rb")
        if game is None:
            game = action_file.split(os.sep)[-1].split(".")[0]
        self.env = self.get_env(game)

    def get_env(self, game):
        """Initialize the game environment.
        
        Params:
            game - the name of the game environment

        Returns: the gym environment
        """
        env = gym.make(game)
        env.seed(1)
        env = gym.wrappers.ResizeObservation(env, (84, 84))
        env = gym.wrappers.GrayScaleObservation(env)
        return gym.wrappers.FrameStack(env, 4)

    def get_returns(self, returns_file):
        """Load and scale the returns from a file.
        
        Params:
            returns_file - the path to the .npy file containing the returns

        Returns: the returns scaled to [0, 1]
        """
        data = np.load(returns_file)
        max_val, min_val = np.max(data), np.min(data)
        scale = max_val - min_val
        if scale == 0.:
            scale = 1.
        return (data - min_val) / scale

    def train_gen(self, limit):
        """Generate training samples for a number of runs.
        
        Params:
            limit - the number of game iterations (runs) used for training

        Yields: (obs, return)
            obs - the (4, 84, 84) image stack as a numpy array
            return - the scaled return for the corresponding timestep
        """
        n = -1
        self.reset_file()
        byte = self.file.read(1)
        while True:
            if byte == b'R':
                # Run finished
                obs, info = self.env.reset()
                n += 1
                if n == limit:
                    return
            else:
                # Yield observation
                obs, r, done, _,_ = self.env.step(ord(byte) - 97)
                self.i += 1
                yield np.array(obs), self.returns[self.i]
            byte = self.file.read(1)

    def test_gen(self):
        """Generate test samples until the end of the file.
        
        Yields: (obs, return)
            obs - the (4, 84, 84) image stack as a numpy array
            return - the scaled return for the corresponding timestep
        """
        byte = self.file.read(1)
        while byte != b"":
            if byte == b'R':
                obs, info = self.env.reset()
            else:
                obs, r, done, _,_ = self.env.step(ord(byte) - 97)
                self.i += 1
                yield np.array(obs), self.returns[self.i]
            byte = self.file.read(1)
        return
    

    def gen(self):
        """Return a generator to generate train or test samples.
        NOTE: Alternates between producing train and test generators each time it is called.

        Returns: a generator yielding (obs, return) pairs where obs is a (4, 84, 84) numpy image stack
        """
        if self.train:
            gen = self.train_gen(self.train_n)
        else:
            gen = self.test_gen()
        self.train = not self.train
        return gen

    def reset_file(self):
        """Reset the actions file at the beginning of an epoch."""
        self.file.seek(0)
        self.env.reset(seed=1)
        self.i = -1

    def get_split(self, val_ratio):
        """Return a dataset that allows train/test split iteration.
        
        Params:
            val_ratio - the proportion of samples to use in the test split
        
        Returns: (ds, ds)
            ds - a generator dataset that alternates between producing train and test samples each time iteration starts
                NOTE: Always alternate between training and validation when using this dataset!
        """
        self.train = True
        n = self.file.read().count(b'R')
        self.train_n = int(n * (1 - val_ratio))
        spec = (tf.TensorSpec(shape=(4, 84, 84), dtype=tf.uint8), tf.TensorSpec(shape=(), dtype=tf.float32))
        ds = tf.data.Dataset.from_generator(self.gen, output_signature=spec)
        ds = self.prepare([ds])[0]
        return ds, ds