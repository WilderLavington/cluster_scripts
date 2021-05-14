
import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.spaces.discrete import Discrete
from gym.spaces.box import Box as Continuous

class TemplateEnv(gym.Env):
  metadata = {'render.modes': ['human','rgb_array']}
  
  def __init__(self):
      self._max_episode_steps = None
      self.action_space = None
      self.observation_space = None
      self.seed = None
    
  def step(self, action):
    ...
  def reset(self):
    ...
  def render(self, mode='human', close=False):
    ...
