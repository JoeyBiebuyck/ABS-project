import numpy as np
import time
import util
import grid_classes
import decentralised_agent
import visual_grid

class Grid(object):  # het logische grid
    def __init__(self, item_to_pos_dict, size, strategy=util.random_action, laadplatformen=2, nr_of_agents=2, cell_size=30):
        self.agents = [decentralised_agent.Agent(self, strategy, i) for i in range(nr_of_agents)]  # init hier x agenten, (hier veronderstellen we dat het aantal agenten nooit groter zal zijn dan het aantal kolommen in de grid)
        self.items_to_pos_dict = item_to_pos_dict
        self.logic_grid: np.ndarray[np.ndarray[grid_classes.Position]] = np.array([np.array([grid_classes.Position() for _ in range(size)]) for _ in range(size)])
        self.grid_ui = visual_grid.GridUI(size, cell_size)
        self.size = size
        self.cell_size = cell_size
        self.init_on_curr_pos = False    # deze variabele bepaalt of de nieuwe agenten die oude agenten zouden vervangen beginnen op de startposities, of op de posities waar de oude agenten laatst stonden.
        self.running = True              # als ze niet op de startpositie komen te staan, dan mogen er (in deze versie) niet meer agenten worden toegevoegd dan er worden weggehaald.
        self.nr_of_orders = 0

        #self.grid_ui.canvas.bind("<Button-1>", self.move_up)

    def find(self, item_name):  # functie om te vinden waar een item is in de grid
        return self.items_to_pos_dict(item_name)

    def has_item(self, position, list_of_items): # kijkt of er op een positie een item die in list of items zit
        row, col = position
        item = self.logic_grid[row][col].item
        return item in list_of_items

    def is_loading_dock(self, position, agent):  # de positie een loading dock van een agent is
        row, col = position
        loading_dock = self.logic_grid[row][col].loading_dock
        if loading_dock is not None:
            owner_of_dock = loading_dock.agent
            if owner_of_dock is not None:
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
            self.logic_grid[row][col].loading_dock = grid_classes.Loading_Dock(agent, agent.starting_position)
            self.logic_grid[row][col].agent = agent
            print(f"Added agent at position ({row}, {col}) with loading dock")

   #     self.grid_ui.update_ui(self.logic_grid)  # updating method!!!

    def replace_agents(self, new_agents, old_agents):  # functie die kapotte agents verwijdert en toevoegt (agent weg en toe voegen) TODO: moet aan de nieuwe uitbreidingen aangepast worden
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
                    self.logic_grid[starting_row][starting_col].loading_dock = grid_classes.Loading_Dock(agent, agent.starting_position)
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
                    self.logic_grid[starting_row][starting_col].loading_dock = grid_classes.Loading_Dock(agent, agent.starting_position)
                    self.logic_grid[starting_row][starting_col].agent = agent

        for agent in self.agents:
            other_agents = self.agents.copy()
            other_agents.remove(agent)
            agent.other_agents = other_agents
            agent.available += old_choices # voeg de gedepositte items toe aan de available items
    #       self.grid_ui.update_ui(self.logic_grid)  # updating method!!!

    def broadcast_order(self, order): # laat aan elke agent weten wat de order is
        self.nr_of_orders += 1
        for agent in self.agents:
            if self.nr_of_orders == 1:
                agent.current_order = 1
                agent.highest_order = 1
                agent.available = order.copy()
                agent.original_orders[agent.highest_order] = order.copy()
                agent.developing_orders[agent.highest_order] = order.copy()
            else:
                agent.highest_order += 1
                agent.original_orders[agent.highest_order] = order.copy()
                agent.developing_orders[agent.highest_order] = order.copy()

    # fase waar agenten kiezen voor welke items ze moeten gaan.
    def play(self):  # roept play op bij elke agent
        while self.running:
            for agent in self.agents:
                agent.play()
            self.grid_ui.update_ui(self.logic_grid)
            time.sleep(0.1)

    def stop(self):
        self.running = False