from enum import Enum
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
import random

def random_action(list_of_items):
    return random.choice(list_of_items)


class GridUI(tk.Tk):  # voor de visualisatie
    def __init__(self, size, cell_size):
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
        images = ["apple.png", "peach.png", "banana.png", "strawberry.png"]

        for i in range(self.size):
            for j in range(self.size):
                pos = logic_grid[i][j]
                if pos.agent:
                    self.add_image_to_grid(i, j, "agent.png")
                elif pos.item:
                    image = random.choice(images)
                    images.remove(image)
                    self.add_image_to_grid(i, j, image) #item.png
                elif pos.loading_dock:
                    self.add_image_to_grid(i, j, "loading_dock.png")
                else:
                    if (i, j) in self.images:
                        self.canvas.delete(self.images[(i, j)])
                        del self.images[(i, j)]


class Grid(object):  # het logische grid
    def __init__(self, item_to_pos_dict, size, strategy=random_action, laadplatformen=2, nr_of_agents=2, cell_size=30):
        self.agents = [Agent(self, strategy) for _ in range(nr_of_agents)]  # init hier x agenten, (hier veronderstellen we dat het aantal agenten nooit groter zal zijn dan het aantal kolommen in de grid)
        self.items_to_pos_dict = item_to_pos_dict
        self.logic_grid: np.ndarray[np.ndarray[Position]] = np.array([np.array([Position() for _ in range(size)]) for _ in range(size)])
        self.grid_ui = GridUI(size, cell_size)
        self.size = size
        self.cell_size = cell_size
        self.init_on_curr_pos = False    # deze variabele bepaalt of de nieuwe agenten die oude agenten zouden vervangen beginnen op de startposities, of op de posities waar de oude agenten laatst stonden.
                                        # als ze niet op de startpositie komen te staan, dan mogen er (in deze versie) niet meer agenten worden toegevoegd dan er worden weggehaald.

        #self.grid_ui.canvas.bind("<Button-1>", self.move_up)

    def find(self, item_name):  # functie om te vinden waar een item is in de grid
        return self.items_to_pos_dict(item_name)

    # def move_up(self, event):
    #     row = event.y // self.cell_size
    #     col = event.x // self.cell_size
    #     print(row,col)
    #     agent = self.logic_grid[row][col].agent
    #     print(agent)
    #     if agent is None:
    #         print("none")
    #     elif self.logic_grid[row][col].loading_dock is not None:
    #         print("Loading_dock!")
    #         agent.move((row - 1, col))
    #         self.grid_ui.update_ui(self.logic_grid)
    #
    #     else:
    #         agent.move((row - 1, col))
    #         self.grid_ui.update_ui(self.logic_grid)

    def has_item(self, position, list_of_items): # kijkt of er op een positie een item die in list of items zit
        row, col = position
        item = self.logic_grid[row][col].item
        return item in list_of_items

    def is_loading_dock(self, position, agent): # loading dok is specifiek aan een agent is
        row, col = position
        loading_dock = self.logic_grid[row][col].loading_dock
        return loading_dock.agent == agent

    def init_agents(self):  # geeft de agenten hun startpositie en een lijst van andere agenten
        current_starting_pos = 0
        for agent in self.agents:
            other_agents_list = self.agents.copy()
            other_agents_list.remove(agent)
            agent.other_agents = other_agents_list
            agent.starting_position = (self.size-1, current_starting_pos)
            agent.current_position = agent.starting_position
            current_starting_pos += 1

    def populate_grid(self):  # vul de grid met alle agenten, items en loading docks in logic grid
        for key, value in self.items_to_pos_dict.items():  # populate de items
            row, col = value
            self.logic_grid[row][col].item = key
            print(f"Added item '{key}' at position ({row}, {col})")
        for agent in self.agents:  # populate de laadplekken en agenten
            row, col = agent.starting_position
            self.logic_grid[row][col].loading_dock = Loading_Dock(agent, agent.starting_position)
            self.logic_grid[row][col].agent = agent
            print(f"Added agent at position ({row}, {col}) with loading dock")

        self.grid_ui.update_ui(self.logic_grid)  # updating method!!!

    def replace_agents(self, new_agents, old_agents):  # functie die kapotte agents verwijdert en toevoegt (agent weg en toe voegen)
        starting_positions = []
        current_positions = []
        old_choices = []

        for agent in old_agents:
            self.agents.remove(agent) # haal de agent weg uit de lijst agenten
            curr_row, curr_col = agent.current_position
            starting_row, starting_col = agent.starting_position
            starting_positions.append((starting_row, starting_col)) # sla zijn startpositie op
            current_positions.append((curr_row, curr_col))  # sla zijn huidige positie op
            old_choices.append(agent.chosen_items) # alle items dat hij op zich had gaan verloren, onthou welke hij gereserveerd had
            self.logic_grid[curr_row][curr_col].agent = None
            self.logic_grid[starting_row][starting_col].loading_dock = None

        if self.init_on_curr_pos:  # bepaald of je nieuwe agenten initialiseert op een startpositie of op de huidige locatie van een verwijderde agent
            positions = zip(starting_positions, current_positions)
            for agent in new_agents:
                self.agents.append(agent)
                if not len(positions) == 0: # safety check
                    starting_pos, current_pos = positions.pop()
                    agent.starting_position = starting_pos
                    agent.current_position = current_pos
                    starting_row, starting_col = starting_pos
                    curr_row, curr_col = current_pos
                    self.logic_grid[starting_row][starting_col].loading_dock = Loading_Dock(agent, agent.starting_position)
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
                    self.logic_grid[starting_row][starting_col].loading_dock = Loading_Dock(agent, agent.starting_position)
                    self.logic_grid[starting_row][starting_col].agent = agent

        for agent in self.agents:
            other_agents = self.agents.copy()
            other_agents.remove(agent)
            agent.other_agents = other_agents
            agent.available += old_choices # voeg de gedepositte items toe aan de available items
        self.grid_ui.update_ui(self.logic_grid)  # updating method!!!

    def broadcast_order(self, order): # laat aan elke agent weten wat de order is
        for agent in self.agents:
            agent.available.append(order)

    # fase waar agenten kiezen voor welke items ze moeten gaan.
    def play(self): # roept play op bij elke agent
        while True:
            for agent in self.agents:
                agent.play()



class Agent(object):
    def __init__(self, grid, strategy, capacity=2):  # TODO: zorg ervoor dat elke strategie dezelfde parameters neemt (en definieer ze altijd boven alles)
        self.starting_position: (int, int) = (-1, -1)  # is dezelfde locatie als het laadplatform, filler start positie
        self.current_position: (int, int) = (-1, -1)  # filler positie
        self.other_agents: list[Agent] = [] #lijst van pointers naar de andere agenten
        self.capacity = capacity #storage van een agent
        self.storage = [] # wat zit er al in de storage
        self.strategy = strategy #welke strategie
        self.grid: Grid = grid # logic grid
        self.path = [] # het pad dat de agent moet volgen, sequentie van coordinaten, bevat alles van laadpunt terug tot aan zijn laadpunt
        self.available: list[Product] = [] # items van de order die nog niet gereserveerd zijn
        self.chosen_items: list[Product] = []# items die agent zelf koos
        self.other_agents_choices: list[Product] = [] #items die andere agents kozen
        self.highest_order = 0
        self.current_order = 0
        self.original_orders = {}  # dict van order number -> originele order
        self.developing_orders = {}  # dict van order number → items van de order dat nog niet gedeposit zijn


    #TODO: pad maken om heen te gaan naar een item en dan nieuw pad om terug te gaan naar laadplatform?
    #TODO: beurt of geen beurt om een item te pakken? -> momenteel wel beurt!
    #TODO: Beschouw pad als heen en terug ? -> momenteel wel!
    #TODO: elke beurt pad berekenen? -> momenteel niet
    def play(self): #kies actie
        if self.capacity > len(self.chosen_items) and len(self.available) != 0 and len(self.storage) == 0: # als je nog items kan "reserveren", doe dat
            self.choose_item()
        # elif len(self.path) == 0 and len(self.storage) == 0: # als je geen items meer kan reserveren en nog geen pad hebt, maak er een
        #     self.make_path()
        elif self.grid.has_item(self.current_position, self.chosen_items): # als je op een positie bent waar een item is dat je nodig hebt, raap het op
            self.pick_up()
        elif self.grid.is_loading_dock(self.current_position, self) and len(self.storage) != 0: # als je op je loading dock bent, deposit je items
            self.deposit()
        else:
            self.move(self.path[0]) #eerste coordinaat in path

    def make_path(self):
        pass


    def pick_up(self):
        row, col = self.current_position
        item = self.grid.logic_grid[row][col].item
        self.chosen_items.remove(item)
        self.storage.append(item)

    def deposit(self):
        row, col = self.current_position
        item = self.storage.pop()
        loading_dock = self.grid.logic_grid[row][col].loading_dock
        loading_dock.contents.append(item)
        curr_to_deposit = self.developing_orders[self.current_order]
        curr_to_deposit.remove(item)
        self.developing_orders[self.current_order] = curr_to_deposit
        if len(curr_to_deposit) == 0: # laat iedereen naar het volgende order gaan als de andere compleet is TODO: laten we ze misschien al items van andere bestellingen verzamelen?
            self.next_order()
            for agent in self.other_agents:
                agent.next_order()


    def choose_item(self):
        item = self.strategy(self.available)  # verander hier de keuze methode
        self.available.remove(item)
        self.chosen_items.append(item)
        for agent in self.other_agents:
            agent.available.remove(item)
            agent.other_agents_choices.append(item)

    def move(self, position): #checkt of je ergens effectief naar toe kan en beweegt en verwijderd uit pad
        new_row, new_col = position
        if adjacent(self.current_position, position) and self.grid.logic_grid[new_row][new_col].agent is None:
            self.path.remove(position)
            if not out_of_bounds(position, self.grid.size):
                curr_row, curr_col = self.current_position
                self.grid.logic_grid[curr_row][curr_col].agent = None
                self.grid.logic_grid[new_row][new_col].agent = self
                self.current_position = position
                self.grid.grid_ui.update_ui(self.grid.logic_grid)  # updating method!!!


    def next_order(self):
        if self.highest_order > self.current_order:
            self.current_order += 1



class Product(object):
    def __init__(self, name, weight=0, height=0, width=0, depth=0):
        self.name = name
        self.weight = weight
        self.volume = height * width * depth


class Loading_Dock(object):
    def __init__(self, agent, position):
        self.agent = agent
        self.position = position
        self.contents = []


class Position(object):
    def __init__(self):
        self.agent = None
        self.loading_dock = None
        self.item = None


def adjacent(pos1, pos2):
    row1, col1 = pos1
    row2, col2 = pos2
    return abs(row1 - row2) == 1 ^ abs(col1 - col2) == 1

def out_of_bounds(pos, size):
    row, col = pos
    return row < 0 or row > size-1 or col < 0 or col > size-1


def build_dictionary(lijst_van_producten, grid_size): # bouwt item to position dictionary
    dict = {}
    taken_pos: list[(int, int)] = []
    for product in lijst_van_producten:
        while True:
            new_pos = generate_random_coordinate(0, grid_size - 2, 0,
                                                 grid_size - 1)  # onderste rij is gereserveerd voor load docks
            if new_pos not in taken_pos:
                taken_pos.append(new_pos)
                dict[product] = new_pos
                break
    return dict

def initialize_grid(size, product_list):
    positions = build_dictionary(product_list, size)
    grid = Grid(positions, size)
    grid.populate_grid()
    return grid


def generate_random_coordinate(min_row, max_row, min_col, max_col): # bouwt item to position dictionary
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
    item1 = Product("item1")
    item2 = Product("item2")
    item3 = Product("item3")
    producten_lijst = [item1, item2, item3]
    item_dict = build_dictionary(producten_lijst, grid_size)
    order = generate_order(producten_lijst)
    main_grid = Grid(item_dict, grid_size)
    main_grid.init_agents()
    main_grid.populate_grid()
    main_grid.broadcast_order(order)
    # main_grid.play()



    # my_print(logic_grid.logic_grid)
    main_grid.grid_ui.mainloop()
