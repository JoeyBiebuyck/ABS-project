from enum import Enum
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk


class GridUI(tk.Tk):  # voor de visualisatie
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

class Grid(object):  # het logische grid
    def __init__(self, item_to_pos_dict, size, cell_size=30, laadplatformen=2, nr_of_agents=2):
        self.agents = []  # init hier x agenten, (hier veronderstellen we dat het aantal agenten nooit groter zal zijn dan het aantal kolommen in de grid)
        self.items_to_pos_dict = item_to_pos_dict
        self.empty_item = Item()
        self.logic_grid = np.array([np.array([self.empty_item for _ in range(size)]) for _ in range(size)])  # TODO: moet gepopulate worden met de agenten, laadplekken en voorwerpen

    def find(self, item_name): # functie om te vinden waar een item is in de grid
        return self.items_to_pos_dict(item_name)

    def init_agents(self):  # geef de agenten hun startpositie en een lijst van andere agenten
        current_starting_pos = 0
        for agent in self.agents:
            other_agents_list = self.agents.remove(agent)
            agent.other_agents = other_agents_list
            agent.starting_position = (current_starting_pos, 0)
            agent.current_position = agent.starting_position
            current_starting_pos += 1

    def populate_grid(self): # vul de grid met alle agenten, items en loading docks
        for key, value in self.items_to_pos_dict.items():
            x, y = value
            self.logic_grid[x][y] = key
        for agent in self.agents:
            x, y = agent.starting_position
            self.logic_grid[x][y] = Loading_dock(agent, agent.starting_position)

class Agent(object):
    def __init__(self, capacity=2):
        self.goals = []
        self.path = None
        self.available = None
        self.other_agents = None
        self.starting_position = None  # is dezelfde locatie als het laadplatform
        self.current_position = None

    def choose_item(self):
        self.goals.append()


class Item(object):
    def __init__(self, weight=0, height=0, width=0, depth=0):
        self.weight = weight
        self.volume = height * width * depth

class Loading_dock(object):
    def __init__(self, agent, position):
        self.agent = agent
        self.position = position



if __name__ == "__main__":
    grid_ui = GridUI(10)
    grid_ui.mainloop()
