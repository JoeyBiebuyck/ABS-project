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
        self.images = {}  # als dictionary initialiseren

    def add_image_to_grid(self, row, col, image_path):

        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            print("Invalid grid position.")
            return
        x0 = col * self.cell_size
        y0 = row * self.cell_size
        if (row, col) in self.images:
            self.canvas.delete(self.images[(row, col)])
        self.images[(row, col)] = tk.PhotoImage(file=image_path)
        # tot nu toe kunnen we die afbeelding aan de grid toevoegen maar we moeten die nog scalen tot een grid cell

        original_image = tk.PhotoImage(file=image_path)
        # Hier berekenen we de scaling factors om de afbeelding te fitten in  de cell net zoals gedaan in OOP taak
        scale_x = self.cell_size / original_image.width()
        scale_y = self.cell_size / original_image.height()

        # De kleinste van de scales wordt gebruikt om een aspect ratio te behouden
        scale_factor = min(scale_x, scale_y)

        # Nu kan er gemakkelijk worden genormaliseerd
        resized_image = original_image.subsample(int(1 / scale_factor))
        self.images[(row, col)] = resized_image
        self.canvas.create_image(x0 + self.cell_size // 2, y0 + self.cell_size // 2, image=resized_image)

    def draw_grid(self, images=None):
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
        self.grid_ui = GridUI(size)
        self.size = size

    def find(self, item_name): # functie om te vinden waar een item is in de grid
        return self.items_to_pos_dict(item_name)

    def init_agents(self):  # geef de agenten hun startpositie en een lijst van andere agenten
        current_starting_pos = 0
        for agent in self.agents:
            other_agents_list = self.agents.remove(agent)
            agent.other_agents = other_agents_list
            agent.starting_position = (current_starting_pos, self.size)
            agent.current_position = agent.starting_position
            current_starting_pos += 1

    def populate_grid(self): # vul de grid met alle agenten, items en loading docks
        for key, value in self.items_to_pos_dict.items(): # populate de items
            x, y = value
            self.logic_grid[x][y].item = key
            self.grid_ui.add_image_to_grid(x, y, "download.png")
        for agent in self.agents: # populate de laadplekken en agenten
            x, y = agent.starting_position
            self.logic_grid[x][y].loading_dock = Loading_dock(agent, agent.starting_position)
            self.logic_grid[x][y].agent = agent

    def update_agents(self, new_agents, old_agents): # functie die kapotte agents verwijdert en toevoegt
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
        self.path = []
        self.available = []
        self.other_agents = []
        self.other_agents_choices = []
        self.starting_position = (-1, -1)  # is dezelfde locatie als het laadplatform, filler start positie
        self.current_position = (-1, -1) # filler positie

    def choose_item(self):
        item = random.choice(self.available) # verander hier de keuze methode
        self.available.remove(item)
        self.goals.append(item)
        for agent in self.other_agents:
            agent.available.remove(item)
            agent.other_agents_choices.append(item)

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

def generate_positions(lijst_van_producten, grid_size):
    dict = {}
    for product in lijst_van_producten:
        x = random.randint(0, grid_size-1)
        y = random.randint(0, grid_size-2)  # onderste rij is gereserveerd voor load docks
        dict[product] = (x, y)
    return dict

def generate_order(lijst_van_producten, length_of_order=6):
    order = []
    for _ in range(length_of_order):
        order.append(random.choice(lijst_van_producten))
    return order


if __name__ == "__main__":
    grid_size = 5
    item1 = Item("item1")
    item2 = Item("item2")
    item3 = Item("item3")
    producten_lijst = [item1, item2, item3]
    item_dict = generate_positions(producten_lijst, grid_size)
    order = generate_order(producten_lijst)
    logic_grid = Grid(item_dict, grid_size)
    logic_grid.init_agents()
    logic_grid.populate_grid()
    logic_grid.grid_ui.mainloop()

    # grid_ui = GridUI(10)
    # grid_ui.add_image_to_grid(2, 3, "download.png")
    # grid_ui.mainloop()
