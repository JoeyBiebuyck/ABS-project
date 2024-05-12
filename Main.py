from enum import Enum
import numpy as np
from matplotlib import pyplot as plt

class Grid(object):
   def __init__(self, item_to_pos_dict, size, laadplatformen=1, nr_of_agents=2):
      self.agents = [] # init hier x agenten
      self.items_to_pos_dict = item_to_pos_dict

   def find(self, item_name):
      return self.items_to_pos_dict(item_name)

class Agent(object):
   def __init__(self, capacity=2):
      self.goals = []
      self.path = None
      self.available = None
      self.other_agents = None

   def choose_item(self):
      self.goals.append()