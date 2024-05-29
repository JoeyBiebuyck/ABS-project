import numpy as np
import random
import math

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
        else: return False

def random_action(list_of_items):
    return random.choice(list_of_items)

def manhattandistance(a, b): # berekent manhattan distance
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
def neighbours(loc, grid):  # nodig voor A-star, basically successor
    return filter(lambda coordinate: grid.logic_grid[coordinate[0]][coordinate[1]].agent is None, filter(lambda coordinate: not out_of_bounds(coordinate, grid.size), [(loc[0]-1, loc[1]), (loc[0]+1, loc[1]), (loc[0], loc[1]+1), (loc[0], loc[1]-1)]))

def astar(grid, start, goal): # maakt een pad tussen start en goal
    agenda = PriorityQueue()
    agenda.insert(0, (start, [], 0))
    visited = []
    while True:
        if not agenda.empty():
            current_pos, path, cost = agenda.serve()
            print("start and finish: ", start, goal)
            print("current path: ", path)
            if not current_pos in visited:
                visited.append(current_pos)
                if current_pos == goal:
                    print("THE PATH WE FOUND IS: ", path)
                    if len(path) == 0:  # als er het pad 1 lang is, en er staat een agent op de goal, geef de huidige positie terug (de start positie) zodat de agent niet beweegt
                        [start]
                    else:
                        return path
                for neighbour in neighbours(current_pos, grid):
                    cost = cost + 1
                    new_path = path + [neighbour]
                    heuristic = math.dist(neighbour, goal)
                    total_cost = cost + heuristic
                    agenda.insert(total_cost, (neighbour, new_path, cost))
        else:
            print("SOMETHING WENT TERRIBLY WRONG")
            print("")
            break

def move_right(pos, next_pos, grid_size):  # berekent de positie rechts van de richting waar de agent in gaat
    pot_next_pos = []
    if next_pos[0] == pos[0] + 1:
        pot_next_pos = [pos[0], pos[1] + 1]
    elif next_pos[0] == pos[0] - 1:
        pot_next_pos = [pos[0], pos[1] - 1]
    elif next_pos[1] == pos[1] + 1:
        pot_next_pos = [pos[0] + 1, pos[1]]
    elif next_pos[1] == pos[1] - 1:
        pot_next_pos = [pos[0] - 1, pos[1]]

    if out_of_bounds(pot_next_pos, grid_size):
        return pos
    else: return pot_next_pos

def adjacent(pos1, pos2):
    row1, col1 = pos1
    row2, col2 = pos2
    return abs(row1 - row2) <= 1 ^ abs(col1 - col2) <= 1

def out_of_bounds(pos, size):
    row, col = pos
    return row < 0 or row > size-1 or col < 0 or col > size-1

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
