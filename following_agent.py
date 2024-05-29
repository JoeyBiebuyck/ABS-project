# agent moet gwn kunnen moven dingen op pakken en depositten, de rest zou door de bigdog moeten bepaald worden?
#zoals bijvoorbeeld wanneer te moeten oppakken of neerzetten.
import logic_grid
import grid_classes
import util
class small_brain_agent(object):
    def __init__(self, grid, name, capacity=2):
        self.starting_position: (int, int) = (-1, -1)  # is dezelfde locatie als het laadplatform, filler start positie
        self.current_position: (int, int) = (-1, -1)
        self.capacity = capacity
        self.storage = []
        self.grid: logic_grid.Grid = grid  # logic grid
        self.available: list[grid_classes.Product] = []  # items van de order die nog niet gereserveerd zijn
        self.name = "Agent " + str(name)

    def move(self, next_pos):
        curr_pos_row, curr_pos_col = self.current_position
        next_pos_row, next_pos_col = next_pos
        # als er geen agent is gaan we gwn naar de volgende positie
        if not util.out_of_bounds(next_pos, self.grid.size):
            self.grid.logic_grid[curr_pos_row][curr_pos_col].agent = None
            self.grid.logic_grid[next_pos_row][next_pos_col].agent = self
            self.current_position = next_pos

    def pick_up(self):
        row, col = self.current_position
        item = self.grid.logic_grid[row][col].item
        self.storage.append(item)

    def deposit(self):
        print(self.name, " depositing")
        row, col = self.current_position
        item = self.storage.pop()
        loading_dock = self.grid.logic_grid[row][col].loading_dock
        loading_dock.contents.append(item)