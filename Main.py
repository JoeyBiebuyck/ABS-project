from enum import Enum
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk


class GridUI(tk.Tk):
   def __init__(self, size, cell_size=30):
      super().__init__()
      self.size = size
      self.cell_size = cell_size
      self.canvas = tk.Canvas(self, width=size * cell_size, height=size * cell_size)
      self.canvas.pack()
      self.draw_grid()

   def draw_grid(self):
      for i in range(self.size):
         for j in range(self.size):
            x0 = j * self.cell_size
            y0 = i * self.cell_size
            x1 = x0 + self.cell_size
            y1 = y0 + self.cell_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")


class Grid(object):
   def __init__(self, item_to_pos_dict, size, cell_size=30, laadplatformen=2, nr_of_agents=2):
      self.agents = [] # init hier x agenten
      self.items_to_pos_dict = item_to_pos_dict # TODO: maak de dictionary
      self.logic_grid = np.array([np.array(None) for i in range(size)]) # TODO: moet gepopulate worden met de agenten, laadplekken en voorwerpen

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

if __name__ == "__main__":
   grid_ui = GridUI(10)
   grid_ui.mainloop()