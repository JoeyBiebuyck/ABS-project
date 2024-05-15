from enum import Enum
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
import random


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
        self.agents = [Agent(self) for _ in range(nr_of_agents)]  # init hier x agenten, (hier veronderstellen we dat het aantal agenten nooit groter zal zijn dan het aantal kolommen in de grid)
        self.items_to_pos_dict = item_to_pos_dict
        self.logic_grid = np.array([np.array([Position() for _ in range(size)]) for _ in range(size)])
        self.grid_ui = GridUI(10)

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
        for key, value in self.items_to_pos_dict.items(): # populate de items
            x, y = value
            self.logic_grid[x][y].item = key
        for agent in self.agents: # populate de laadplekken en agenten
            x, y = agent.starting_position
            self.logic_grid[x][y].loading_dock = Loading_dock(agent, agent.starting_position)
            self.logic_grid[x][y].agent = agent

    def update_agents(self, new_agents, old_agents): # functie die kapotte agents verwijderd en toevoegd
        starting_positions = []
        for agent in old_agents:
            self.agents.remove(agent)
            x_curr, y_curr = agent.current_position
            x_starting, y_starting = agent.starting_position
            starting_positions.append(agent.starting_position)
            self.logic_grid[x_curr][y_curr].agent = None
            self.logic_grid[x_starting][y_starting].loading_dock = None
        for agent in new_agents:
            self.agents.append(agent)
            if not len(starting_positions) == 0:
                agent.starting_position = starting_positions.pop()
                x, y = agent.starting_position
                self.logic_grid[x][y].loading_dock = Loading_dock(agent, agent.starting_position)
                agent.current_position = agent.starting_position # pas hier de positie aan als de agent niet begint op de loading dock
        for agent in self.agents:
            other_agents = self.agents.remove(agent)
            agent.other_agents = other_agents

class Agent(object):
    def __init__(self, grid, strategy="random", capacity=2): # TODO: maak het zodat je gemakkelijk strategies kan veranderen
        self.goals = []
        self.strategy = strategy
        self.grid = grid
        self.path = None
        self.available = None
        self.other_agents = None
        self.starting_position = (-1, -1)  # is dezelfde locatie als het laadplatform, filler start positie
        self.current_position = None

    def choose_item(self):
        item = random.choice(self.available) # verander hier de keuze methode
        self.available.remove(item)
        self.goals.append(item)
        for agent in self.other_agents:
            agent.available.remove(item)

    def move(self, position):
        if adjacent(self.current_position, position) and self.grid.logic_grid.agent is None:
            x_curr, y_curr = self.current_position
            x_new, y_new = position
            self.grid.logic_grid[x_curr][y_curr].agent = None
            self.grid.logic_grid[x_new][y_curr].agent = self


class Item(object):
    def __init__(self, name, weight=0, height=0, width=0, depth=0):
        self.name = name
        self.weight = weight
        self.volume = height * width * depth

class Loading_dock(object):
    def __init__(self, agent, position):
        self.agent = agent
        self.position = position

class Position(object):
    def __init__(self):
        self.agent = None
        self.loading_dock = None
        self.item = None

def adjacent(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) == 1 ^ abs(y1 - y2) == 1


if __name__ == "__main__":
    logic_grid = Grid({}, 5)
    logic_grid.init_agents()
    logic_grid.populate_grid()
    logic_grid.grid_ui.mainloop()
