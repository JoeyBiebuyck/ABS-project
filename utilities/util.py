import numpy as np
import random
import math
import pandas as pd

random.seed(1)


# Implementatie van priority queue
class PriorityQueue:
    def __init__(self):
        self.storage = []

    def insert(self, priority, item):
        self.storage.append((priority, item))

    def serve(self):
        if len(self.storage) == 0:
            return print("No items left to serve")
        else:
            item = min(self.storage, key=lambda tuple: tuple[0])
            self.storage.remove(item)
            return item[1]

    def empty(self):
        if len(self.storage) == 0:
            return True
        else:
            return False


# Functie die een willekeurig item uit een lijst kiest
def random_action(list_of_items):
    return random.choice(list_of_items)


# Functie die Manhattan distance berekent
def manhattandistance(a, b):
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


# Functie die de neighbours van een positie berekent, is nodig voor A-star. (basically een successor functie)
def neighbours(loc, grid, goal):
   return filter(lambda coordinate: grid.logic_grid[coordinate[0]][coordinate[1]].agent is None or coordinate == goal,
                 filter(lambda coordinate: not out_of_bounds(coordinate, grid.size),
                        [(loc[0]-1, loc[1]), (loc[0]+1, loc[1]), (loc[0], loc[1]+1), (loc[0], loc[1]-1)]))


# Implementatie van het A-star algoritme
# Genereert een pad tussen start en goal
def astar(grid, start, goal):
    agenda = PriorityQueue()
    agenda.insert(0, (start, [], 0))
    visited = []
    while True:
        if not agenda.empty():
            current_pos, path, cost = agenda.serve()
            if not current_pos in visited:
                visited.append(current_pos)
                if current_pos == goal:
                    if len(path) == 0:  # als er het pad 1 lang is, en er staat een agent op de goal, geef de huidige positie terug (de start positie) zodat de agent niet beweegt
                        return [start]
                    else:
                        return path
                for neighbour in neighbours(current_pos, grid, goal):
                    cost = cost + 1
                    new_path = path + [neighbour]
                    heuristic = math.dist(neighbour, goal)
                    total_cost = cost + heuristic
                    agenda.insert(total_cost, (neighbour, new_path, cost))
        else:
            print("SOMETHING WENT TERRIBLY WRONG")
            print("")
            break


# Functie die de rechtse positie berekent in de richting waar de agent in beweegt (gebruikt bij conflicten)
def move_right(pos, next_pos, grid_size):
    pot_next_pos = []
    if next_pos[0] == pos[0] + 1:
        pot_next_pos = [pos[0], pos[1] + 1]
    elif next_pos[0] == pos[0] - 1:
        pot_next_pos = [pos[0], pos[1] - 1]
    elif next_pos[1] == pos[1] + 1:
        pot_next_pos = [pos[0] + 1, pos[1]]
    elif next_pos[1] == pos[1] - 1:
        pot_next_pos = [pos[0] - 1, pos[1]]

    if len(pot_next_pos) == 0:
        return pos
    elif out_of_bounds(pot_next_pos, grid_size):
        return pos
    else:
        return pot_next_pos


# Functie om te kijken of 2 posities naast elkaar liggen (geeft ook True als het dezelfde positie is)
def adjacent(pos1, pos2):
    row1, col1 = pos1
    row2, col2 = pos2
    return (abs(row1 - row2) <= 1 ^ abs(col1 - col2) <= 1) or pos1 == pos2


# Functie die berekent of een coordinaat out of bounds is voor een gegeven grid size
def out_of_bounds(coordinate, size):
    if not coordinate == 0:
        row, col = coordinate
        return row < 0 or row > size-1 or col < 0 or col > size-1


# Functie die een random coordinaat genereert op basis van de minimale en maximale waarden
def generate_random_coordinate(min_row, max_row, min_col, max_col): # bouwt item to position dictionary
    row = random.randint(min_row, max_row)
    col = random.randint(min_col, max_col)
    return (row, col)


# Functie dat een bestelling - - een lijst van producten - - genereert De unique parameter bepaald of items uit de
# lijst van producten herhaald mogen worden in de bestelling. True = geen herhalingen, False = herhalingen
def generate_order(lijst_van_producten, length_of_order=6, unique=False):
    order = []
    if not unique:
        for _ in range(length_of_order):
            order.append(random.choice(lijst_van_producten))
        return order
    else:
        return random.sample(lijst_van_producten, length_of_order)


# Functie die een product -> coordinate dictionary genereert
def build_dictionary(lijst_van_producten, grid_size):  # bouwt item to position dictionary
    dict = {}
    taken_pos: list[(int, int)] = []
    for product in lijst_van_producten:
        while True:
            new_pos = generate_random_coordinate(0, grid_size - 2, 0,
                                                 grid_size - 1)  # onderste rij is gereserveerd voor load docks, daarom -2
            if new_pos not in taken_pos:
                taken_pos.append(new_pos)
                dict[product] = new_pos
                break
    return dict


# Functie die alle aangrenzende posities van een positie genereert
def adjacent_positions(position):
    row, col = position
    return [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]


# Functie die alle valid moves voor een agent genereert TODO: doe deze 2 weg?
def valid_moves(agent, grid):
    row = 0
    col = 1
    return filter(lambda position: adjacent(position, agent.current_position)
                                   and grid.logic_grid[position[row]][position[col]].agent is None
                                   and not out_of_bounds(position, grid.size),
                  adjacent_positions(agent.current_position))


def distance_to_item_score(distance):
    if distance == 0:
        return 100
    else:
        return max(0, 50 - distance)


# Initialiseer de files voor data collectie voor agenten bij OV1 & OV2
def init_stat_files(agents_names_list, decentralised=True):
    if decentralised:
        result = pd.DataFrame()
        result = result.rename_axis('index')
        rows = ["Turns choosing", "turns moving", "turns waiting", "number of conflicts", "turns picking up",
                "turns depositing", "times going to next order", "total amount of turns"]  # alle features die door de agenten getracked worden

        row_name_dict = {}
        for index, row_name in zip(range(0, len(rows)), rows):
            row_name_dict[index] = row_name

        result["index"] = list(range(0, len(rows)))
        result["row names"] = result["index"].map(row_name_dict)  # maak een kolom met de namen van de features
        result = result.drop(columns=["index"])

        for name in agents_names_list:
            result.to_csv("Decentralised " + name + ".csv")  # initialiseer de file voor elke agent

    else:
        result_workers = pd.DataFrame()
        result_workers = result_workers.rename_axis('index')
        rows = ["turns moving", "turns picking up", "turns depositing"]
        row_name_dict = {}
        for index, row_name in zip(range(0, len(rows)), rows):
            row_name_dict[index] = row_name

        result_workers["index"] = list(range(0, len(rows)))
        result_workers["row names"] = result_workers["index"].map(row_name_dict)
        result_workers = result_workers.drop(columns=["index"])

        for name in agents_names_list:
            result_workers.to_csv("Centralised worker " + name + ".csv")

        result_central = pd.DataFrame()
        result_central = result_central.rename_axis('index')
        rows_central = ["Turns choosing", "turns waiting", "number of conflicts", "times going to next order", "total amount of turns"]
        row_name_dict_central = {}
        for index, row_name in zip(range(0, len(rows_central)), rows_central):
            row_name_dict_central[index] = row_name

        result_central["index"] = list(range(0, len(rows_central)))
        result_central["row names"] = result_central["index"].map(row_name_dict_central)
        result_central = result_central.drop(columns=["index"])
        result_central.to_csv("Centralised decision maker Agent.csv")


# Initialiseer de files voor data collectie over de informatie van elk order bij OV2
def init_stat_files_OV2():
    result = pd.DataFrame()
    result = result.rename_axis('index')
    rows = ["# products", "grid size", "order size", "# agents"]  # maten die variëren bij elk order
    row_name_dict = {}
    for index, row_name in zip(range(0, len(rows)), rows):
        row_name_dict[index] = row_name

    result["index"] = list(range(0, len(rows)))
    result["row names"] = result["index"].map(row_name_dict)
    result = result.drop(columns=["index"])
    result.to_csv("order info.csv")
