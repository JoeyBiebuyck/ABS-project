from enum import Enum
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
import random


def random_action(list_of_items):
    return random.choice(list_of_items)


class GridUI(tk.Tk):  # voor de visualisatie
    def __init__(self, size, cell_size=30):
        super().__init__()
        self.size = size
        self.cell_size = cell_size
        self.canvas = tk.Canvas(self, width=size * cell_size, height=size * cell_size)
        self.canvas.pack()
        self.draw_grid()
        self.images = {}  # als dictionary initialiseren

        #self.canvas.bind("<Button-1>", self.move_up)

    def add_image_to_grid(self, row, col, image_path):

        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            print("Invalid grid position.")
            return
        x0 = col * self.cell_size
        y0 = row * self.cell_size
        if (row, col) in self.images:
            self.canvas.delete(self.images[(row, col)])
        self.images[(row, col)] = tk.PhotoImage(file=image_path)
        # tot nu toe kunnen we die afbeelding aan de grid toevoegen, maar we moeten die nog scalen tot een grid cell

        original_image = tk.PhotoImage(file=image_path)
        # Hier berekenen we de scaling factors om de afbeelding te fitten in de cell net zoals gedaan in OOP taak
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


    def update_ui(self, logic_grid):
        self.canvas.delete("all")
        # Redraw grid
        self.draw_grid()

        for i in range(self.size):
            for j in range(self.size):
                pos = logic_grid[i][j]
                if pos.agent:
                    self.add_image_to_grid(i, j, "Agent.png")
                elif pos.item:
                    self.add_image_to_grid(i, j, "download.png") #item.png
                elif pos.loading_dock:
                    self.add_image_to_grid(i, j, "Pits.png")
                else:
                    if (i, j) in self.images:
                        self.canvas.delete(self.images[(i, j)])
                        del self.images[(i, j)]

    def move_up(self, event):
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        print(row,col)

        agent = logic_grid.logic_grid[row][col].agent

        if agent:
            agent.move((row - 1, col))


class Grid(object):  # het logische grid
    def __init__(self, item_to_pos_dict, size, strategy=random_action, laadplatformen=2, nr_of_agents=2):
        self.agents = [Agent(self, strategy) for _ in range(nr_of_agents)]  # init hier x agenten, (hier veronderstellen we dat het aantal agenten nooit groter zal zijn dan het aantal kolommen in de grid)
        self.items_to_pos_dict = item_to_pos_dict
        self.logic_grid: np.ndarray[np.ndarray[Position]] = np.array([np.array([Position() for _ in range(size)]) for _ in range(size)])
        self.grid_ui = GridUI(size)
        self.size = size
        self.init_on_curr_pos = True    # deze variabele bepaalt of de nieuwe agenten die oude agenten zouden vervangen beginnen op de startposities, of op de posities waar de oude agenten laatst stonden.
                                        # als ze niet op de startpositie komen te staan, dan mogen er (in deze versie) niet meer agenten worden toegevoegd dan er worden weggehaald.

    def find(self, item_name):  # functie om te vinden waar een item is in de grid
        return self.items_to_pos_dict(item_name)

    def init_agents(self):  # geef de agenten hun startpositie en een lijst van andere agenten
        current_starting_pos = 0
        for agent in self.agents:
            other_agents_list = self.agents.copy()
            other_agents_list.remove(agent)
            agent.other_agents = other_agents_list
            agent.starting_position = (self.size-1, current_starting_pos)
            agent.current_position = agent.starting_position
            current_starting_pos += 1

    def populate_grid(self):  # vul de grid met alle agenten, items en loading docks
        for key, value in self.items_to_pos_dict.items():  # populate de items
            row, col = value
            self.logic_grid[row][col].item = key
            print(f"Added item '{key}' at position ({row}, {col})")
            #self.grid_ui.add_image_to_grid(row, col, "download.png") # TODO: deze moet denk ik weg als er een goede mapping bestaat
        for agent in self.agents:  # populate de laadplekken en agenten
            row, col = agent.starting_position
            self.logic_grid[row][col].loading_dock = LoadingDock(agent, agent.starting_position)
            #self.logic_grid[row][col].agent = agent
            print(f"Added agent at position ({row}, {col}) with loading dock")

        #self.grid_ui.add_image_to_grid(row, col, "epic.png")  # TODO: deze moet denk ik weg als er een goede mapping bestaat

        self.grid_ui.update_ui(self.logic_grid)  # updating method!!!

    def update_agents(self, new_agents, old_agents):  # functie die kapotte agents verwijdert en toevoegt
        starting_positions = []
        current_positions = []
        for agent in old_agents:
            self.agents.remove(agent)
            curr_row, curr_col = agent.current_position
            starting_row, starting_col = agent.starting_position
            starting_positions.append((starting_row, starting_col))
            current_positions.append((curr_row, curr_col))
            self.logic_grid[curr_row][curr_col].agent = None
            self.logic_grid[starting_row][starting_col].loading_dock = None
        if self.init_on_curr_pos: # bepaald of je nieuwe agenten initialiseert op een startpositie of op de huidige locatie van een verwijderde agent
            positions = zip(starting_positions, current_positions)
            for agent in new_agents:
                self.agents.append(agent)
                if not len(positions) == 0: # safety check
                    starting_pos, current_pos = positions.pop()
                    agent.starting_position = starting_pos
                    agent.current_position = current_pos
                    starting_row, starting_col = starting_pos
                    curr_row, curr_col = current_pos
                    self.logic_grid[starting_row][starting_col].loading_dock = LoadingDock(agent, agent.starting_position)
                    self.logic_grid[curr_row][curr_col].agent = agent
        else:
            positions = starting_positions
            for agent in new_agents:
                self.agents.append(agent)
                if not len(positions) == 0:  # safety check
                    starting_pos = positions.pop()
                    agent.starting_position = starting_pos
                    agent.current_position = agent.starting_position
                    starting_row, starting_col = starting_pos
                    self.logic_grid[starting_row][starting_col].loading_dock = LoadingDock(agent, agent.starting_position)
                    self.logic_grid[starting_row][starting_col].agent = agent
        for agent in self.agents:
            other_agents = self.agents.copy()
            other_agents.remove(agent)
            agent.other_agents = other_agents
        self.grid_ui.update_ui(self.logic_grid)  # updating method!!!


class Agent(object):
    def __init__(self, grid, strategy, capacity=2):  # TODO: zorg ervoor dat elke strategie dezelfde parameters neemt (en definieer ze altijd boven alles)
        self.goals: list[Item] = []
        self.strategy = strategy
        self.grid: Grid = grid
        self.path = []
        self.available: list[Item] = []
        self.other_agents: list[Agent] = []
        self.other_agents_choices: list[Item] = []
        self.starting_position: (int, int) = (-1, -1)  # is dezelfde locatie als het laadplatform, filler start positie
        self.current_position: (int, int) = (-1, -1)  # filler positie

    def choose_item(self):
        item = self.strategy(self.available)  # verander hier de keuze methode
        self.available.remove(item)
        self.goals.append(item)
        for agent in self.other_agents:
            agent.available.remove(item)
            agent.other_agents_choices.append(item)

    def move(self, position):
        new_row, new_col = position
        if adjacent(self.current_position, position) and self.grid.logic_grid[new_row][new_col].agent is None:
            curr_row, curr_col = self.current_position
            self.grid.logic_grid[curr_row][curr_col].agent = None
            self.grid.logic_grid[new_row][new_col].agent = self
            self.current_position = position
            self.grid.grid_ui.update_ui(self.grid.logic_grid)  # updating method!!!


class Item(object):
    def __init__(self, name, weight=0, height=0, width=0, depth=0):
        self.name = name
        self.weight = weight
        self.volume = height * width * depth


class LoadingDock(object):
    def __init__(self, agent, position):
        self.agent = agent
        self.position = position


class Position(object):
    def __init__(self):
        self.agent = None
        self.loading_dock = None
        self.item = None


def adjacent(pos1, pos2):
    row1, col1 = pos1
    row2, col2 = pos2
    return abs(row1 - row2) == 1 ^ abs(col1 - col2) == 1


def generate_positions(lijst_van_producten, grid_size):
    dict = {}
    taken_pos: list[(int, int)] = []
    for product in lijst_van_producten:
        while True:
            new_pos = generate_position(0, grid_size - 2, 0, grid_size - 1)  # onderste rij is gereserveerd voor load docks
            if new_pos not in taken_pos:
                taken_pos.append(new_pos)
                dict[product] = new_pos
                break
    return dict

def initialize_grid(size, product_list):
    positions = generate_positions(product_list, size)
    grid = Grid(positions, size)
    grid.populate_grid()
    return grid


def generate_position(min_row, max_row, min_col, max_col):
    row = random.randint(min_row, max_row)
    col = random.randint(min_col, max_col)
    return (row, col)


def generate_order(lijst_van_producten, length_of_order=6):
    order = []
    for _ in range(length_of_order):
        order.append(random.choice(lijst_van_producten))
    return order


def my_print(item):
    row, col = item.shape
    for y in range(row):
        for x in range(col):
            print("current coordinate = ", (y, x))


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
    #logic_grid = Grid({}, 5)
    #logic_grid.init_agents()
    #logic_grid.populate_grid()
    logic_grid.grid_ui.mainloop()

    #grid_ui = GridUI(10)
    #grid_ui.add_image_to_grid(2, 3, "download.png")
    #grid_ui.mainloop()

    # products = ["download.png"]
    # grid_size = 10
    # logic_grid = initialize_grid(grid_size, products)
    # logic_grid.grid_ui.mainloop()
    #
    # grid_ui = GridUI(10)
    # grid_ui.add_image_to_grid(2, 3, "download.png")
    # grid_ui.mainloop()
    # my_print(logic_grid.logic_grid)