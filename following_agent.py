# agent moet gwn kunnen moven dingen op pakken en depositten, de rest zou door de bigdog moeten bepaald worden?
#zoals bijvoorbeeld wanneer te moeten oppakken of neerzetten.
import logic_grid
import grid_classes
import util
class following_agent(object):
    def __init__(self, grid, name, capacity=2):
        self.starting_position: (int, int) = (-1, -1)  # is dezelfde locatie als het laadplatform, filler start positie
        self.current_position: (int, int) = (-1, -1)
        self.my_boss = False
        self.capacity = capacity
        self.storage = []
        self.grid: logic_grid.Grid = grid  # logic grid
        self.available: list[grid_classes.Product] = []  # items van de order die nog niet gereserveerd zijn
        self.name = "Agent " + str(name)
        self.appointed_items: list[(grid_classes.Product, int)] = [] #toegewezen items door de centrale agent
        self.current_order = 0
        self.to_get_item = False

        # FOR TESTING:
        self.nr_of_turns_moving = 0
        self.nr_of_turns_picking_up = 0
        self.nr_of_turns_depositing = 0

    def move(self, next_pos):
        self.nr_of_turns_moving += 1
        curr_pos_row, curr_pos_col = self.current_position
        next_pos_row, next_pos_col = next_pos

        # als er geen agent is gaan we gwn naar de volgende positie
        if not util.out_of_bounds(next_pos, self.grid.size):
            self.grid.logic_grid[curr_pos_row][curr_pos_col].agent = None
            self.grid.logic_grid[next_pos_row][next_pos_col].agent = self
            self.current_position = next_pos

    def pick_up(self):
        self.nr_of_turns_picking_up += 1
        row, col = self.current_position
        item = self.grid.logic_grid[row][col].item
        order_nr = -1
        for tuple in self.appointed_items:  # omdat het een lijst van tuples is moet er geïtereerd worden over de lijst om het eerste element van de tuple te matchen, want we willen dat precies 1 tuple verwijderd wordt, niet meerdere
            if tuple[0] == item:
                order_nr = tuple[1]
                self.appointed_items.remove(tuple)
                break
        #  self.chosen_items.remove(item)
        self.storage.append((item, order_nr))
        self.to_get_item = False

    def deposit(self):
        self.nr_of_turns_depositing += 1
        print(self.name, " depositing")
        row, col = self.current_position
        item, order_nr = self.storage.pop()
        loading_dock = self.grid.logic_grid[row][col].loading_dock
        loading_dock.contents.append(item)
        return (item, order_nr)
