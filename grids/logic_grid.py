import numpy as np
from grids import grid_classes
from agents import centralised_agent, decentralised_agent, following_agent
from grids import visual_grid
import pandas as pd
import os
from utilities import globals, util, strategies
import time


# Grid superklasse voor centralised grid en decentralised grid
class Grid(object):
    def __init__(self, item_to_pos_dict, size, cell_size=30, record_stats=False):
        self.items_to_pos_dict = item_to_pos_dict  # item -> positie dictionary
        self.logic_grid: np.ndarray[np.ndarray[grid_classes.Position]] = np.array([np.array([grid_classes.Position() for _ in range(size)]) for _ in range(size)])  # het logische grid
        self.grid_ui = visual_grid.GridUI(size, cell_size)  # het visuele grid
        self.size = size  # grootte van de grid
        self.cell_size = cell_size
        self.init_on_curr_pos = False  # deze variabele bepaalt of de nieuwe agenten die oude agenten zouden vervangen beginnen op de startposities, of op de posities waar de oude agenten laatst stonden.
        self.running = True  # of de play-loop al dan niet moet doorgaan
        self.nr_of_orders = 0  # hoeveel bestellingen er gegeven zijn
        self.record_stats = record_stats  # of de data moet worden opgeslagen voor statistische analyse

    # Methode om te vinden waar een item is in de grid
    def find(self, item_name):
        return self.items_to_pos_dict(item_name)

    # Berekent of er een item uit de lijst op die positie is
    def has_item(self, position, list_of_items):
        row, col = position
        item = self.logic_grid[row][col].item
        return item in list_of_items

    # Berekent of een positie een loading dock is van een bepaalde agent
    def is_loading_dock(self, position, agent):  # de positie een loading dock van een agent is
        row, col = position
        loading_dock = self.logic_grid[row][col].loading_dock
        if loading_dock is not None:
            owner_of_dock = loading_dock.agent
            if owner_of_dock is not None:
                return loading_dock.agent == agent

    # Zet de play-loop stil
    def stop(self):
        self.running = False


# Het grid dat gebruikt wordt voor gedecentraliseerde agenten
class Decentralised_grid(Grid):  # het logische grid
    def __init__(self, item_to_pos_dict, size, strategy=strategies.strategy_1, nr_of_agents=2, cell_size=30, record_stats=False):
        super().__init__(item_to_pos_dict, size, cell_size=cell_size, record_stats=record_stats)
        self.agents = [decentralised_agent.Decentralised_agent(self, strategy, i) for i in range(nr_of_agents)]  # instantieer hier x agenten, (hier veronderstellen we dat het aantal agenten nooit groter zal zijn dan het aantal kolommen in de grid)
        self.init_agents()
        self.populate_grid()

    # Geeft de agenten hun startpositie en een lijst van de andere agenten
    def init_agents(self):
        current_starting_pos = 0
        for agent in self.agents:
            other_agents_list = self.agents.copy()
            other_agents_list.remove(agent)
            agent.other_agents = other_agents_list
            agent.starting_position = (self.size - 1, current_starting_pos)
            agent.current_position = agent.starting_position
            current_starting_pos += 1

    # Vul de grid met alle agenten, items en loading docks in logic grid
    def populate_grid(self):
        for key, value in self.items_to_pos_dict.items():  # populate de items
            row, col = value
            self.logic_grid[row][col].item = key
            print(f"Added item '{key.name}' at position ({row}, {col})")
        print("")
        for agent in self.agents:  # populate de laadplekken en agenten
            row, col = agent.starting_position
            self.logic_grid[row][col].loading_dock = grid_classes.Loading_Dock(agent, agent.starting_position)
            self.logic_grid[row][col].agent = agent
            print(f"Added {agent.name} at position ({row}, {col}) with loading dock")
        print("")

    def replace_agents(self, new_agents, old_agents):  # Methode die kapotte agents verwijdert en toevoegt (agent weg en toe voegen) TODO: moet aan de nieuwe uitbreidingen aangepast worden
        starting_positions = []
        current_positions = []
        old_choices = []

        for agent in old_agents:
            self.agents.remove(agent)  # haal de agent weg uit de lijst agenten
            curr_row, curr_col = agent.current_position
            starting_row, starting_col = agent.starting_position
            starting_positions.append((starting_row, starting_col))  # sla zijn startpositie op
            current_positions.append((curr_row, curr_col))  # sla zijn huidige positie op
            old_choices.append(agent.chosen_items)  # alle items dat hij op zich had gaan verloren, onthou welke hij gereserveerd had
            self.logic_grid[curr_row][curr_col].agent = None
            self.logic_grid[starting_row][starting_col].loading_dock = None

        if self.init_on_curr_pos:  # bepaald of je nieuwe agenten initialiseert op een startpositie of op de huidige locatie van een verwijderde agent
            positions = zip(starting_positions, current_positions)
            for agent in new_agents:
                self.agents.append(agent)
                if not len(positions) == 0:  # safety check
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
            agent.available[agent.current_order] += old_choices  # voeg de gedepositte items toe aan de available items

    # Methode die aan elke agent de informatie over een nieuwe bestelling geeft
    def broadcast_order(self, order):
        self.nr_of_orders += 1
        for agent in self.agents:
            if self.nr_of_orders == 1:
                agent.current_order += 1

            agent.highest_order += 1
            agent.original_orders[agent.highest_order] = order.copy()
            agent.developing_orders[agent.highest_order] = order.copy()
            agent.agent_choices[agent.highest_order] = []
            agent.available_items[agent.highest_order] = order.copy()

    def play(self):  # roept play op bij elke agent
        while self.running:
            for agent in self.agents:
                agent.play()
            self.grid_ui.update_ui(self.logic_grid)  #TODO: uncomment als je wil dat de grid werkt
            time.sleep(0.1)
        if not self.running:  # Geeft de statistieken van elke agent terug als alle bestellingen behandeld zijn
            for agent in self.agents:
                if self.record_stats:
                    result = pd.read_csv("Decentralised " + agent.name + ".csv")
                    all_features = [agent.nr_of_turns_choosing, agent.nr_of_turns_moving, agent.nr_of_turns_waiting, agent.nr_of_conflicts, agent.nr_of_turns_picking_up, agent.nr_of_turns_depositing, agent.nr_of_next_order, agent.total_nr_of_turns]
                    result["Order " + str(globals.order_number)] = all_features
                    os.remove("Decentralised " + agent.name + ".csv")
                    result = result.rename_axis('index')
                    result = result.drop(columns=["index"])
                    result.to_csv("Decentralised " + agent.name + ".csv")

                    if globals.order_info:
                        result_info = pd.read_csv("order info.csv")
                        info_features = [globals.nr_of_products, globals.grid_size, globals.order_size, globals.nr_of_agents]
                        result_info["Order " + str(globals.order_number)] = info_features
                        os.remove("order info.csv")
                        result_info = result_info.rename_axis('index')
                        result_info = result_info.drop(columns=["index"])
                        result_info.to_csv("order info.csv")


            print(agent.name, "statistics: ")
            print("succes! all orders fulfilled\n")
            print("Nr of turns choosing: ", agent.nr_of_turns_choosing)
            print("Nr of turns moving: ", agent.nr_of_turns_moving)
            print("Nr of turns waiting: ", agent.nr_of_turns_waiting)
            print("Nr of conflicts: ", agent.nr_of_conflicts)
            print("Nr of turn picking up items: ", agent.nr_of_turns_picking_up)
            print("Nr of turns depositing: ", agent.nr_of_turns_depositing)
            print("Nr of going to next order:", agent.nr_of_next_order)
            print("Total nr of moves: ", agent.total_nr_of_turns)
            print("")


# Het grid dat gebruikt wordt voor gecentraliseerde agenten
class Centralised_grid(Grid):
    def __init__(self, item_to_pos_dict, size, choose_strategy=strategies.strategy_1, move_strategy=util.astar, nr_of_agents=2, agent_capacity=2, cell_size=30, nr_of_centralised_agents=1, record_stats=False):
        super().__init__(item_to_pos_dict, size, cell_size=cell_size, record_stats=record_stats)
        self.working_agents = [following_agent.following_agent(self, agent_nr, capacity=agent_capacity) for agent_nr in range(nr_of_agents)]  # instantieer hier x werkende agenten, (hier veronderstellen we dat het aantal agenten nooit groter zal zijn dan het aantal kolommen in de grid)
        self.central_agents = [centralised_agent.centralised_agent(self, self.working_agents, choose_strategy, move_strategy, name) for name in range(nr_of_centralised_agents)]  # instantieer hier y centrale agenten
        self.init_agents()
        self.populate_grid()

    # Geeft de agenten hun startpositie en een lijst van de andere agenten
    def init_agents(self):
        current_starting_pos = 0
        for agent in self.working_agents:
            agent.starting_position = (self.size - 1, current_starting_pos)  # gaat de onderste rij af vanaf links en selecteert voor elke agent een startpositie
            agent.current_position = agent.starting_position
            current_starting_pos += 1

    # Vul de grid met alle agenten, items en loading docks in logic grid
    def populate_grid(self):
        for key, value in self.items_to_pos_dict.items():  # populate de items
            row, col = value
            self.logic_grid[row][col].item = key
            print(f"Added item '{key.name}' at position ({row}, {col})")
        print("")
        for agent in self.working_agents:  # populate de laadplekken en agenten, centrale agenten bevinden zich niet op de grid
            row, col = agent.starting_position
            self.logic_grid[row][col].loading_dock = grid_classes.Loading_Dock(agent, agent.starting_position)
            self.logic_grid[row][col].agent = agent
            print(f"Added {agent.name} at position ({row}, {col}) with loading dock")
        print("")

    # Methode die aan elke agent de informatie over een nieuwe bestelling geeft
    def broadcast_order(self, order):
        self.nr_of_orders += 1
        for central_agent in self.central_agents:
            if self.nr_of_orders == 1:
                central_agent.current_order = 1
                for agent in central_agent.working_agents:
                    agent.current_order = 1
            central_agent.highest_order += 1
            central_agent.original_orders[central_agent.highest_order] = order.copy()
            central_agent.developing_orders[central_agent.highest_order] = order.copy()
            central_agent.agent_choices[central_agent.highest_order] = []
            central_agent.available_items[central_agent.highest_order] = order.copy()

    def play(self):
        while self.running:
            for central_agent in self.central_agents:
                central_agent.play()
                self.grid_ui.update_ui(self.logic_grid)  # comment/uncomment om het visuele grid te activeren/desactiveren
                time.sleep(0.1)
        if not self.running:  # Geeft de statistieken van elke agent terug als alle bestellingen behandeld zijn
            for agent in self.working_agents:
                if self.record_stats:
                    result = pd.read_csv("Centralised worker " + agent.name + ".csv")
                    all_features = [agent.nr_of_turns_moving, agent.nr_of_turns_picking_up, agent.nr_of_turns_depositing]
                    result["Order " + str(globals.order_number)] = all_features
                    os.remove("Centralised worker " + agent.name + ".csv")
                    result = result.rename_axis('index')
                    result = result.drop(columns=["index"])
                    result.to_csv("Centralised worker " + agent.name + ".csv")

                print(agent.name, "statistics: ")
                print("Nr of turns moving: ", agent.nr_of_turns_moving)
                print("Nr of turn picking up items: ", agent.nr_of_turns_picking_up)
                print("Nr of turns depositing: ", agent.nr_of_turns_depositing)
                print("")

            for agent in self.central_agents:
                if self.record_stats:
                    result = pd.read_csv("Centralised decision maker Agent.csv")
                    all_features = [agent.nr_of_turns_choosing, agent.nr_of_turns_waiting, agent.nr_of_conflicts, agent.nr_of_next_order, agent.total_nr_of_turns]
                    result["Order " + str(globals.order_number)] = all_features
                    os.remove("Centralised decision maker Agent.csv")
                    result = result.rename_axis('index')
                    result = result.drop(columns=["index"])
                    result.to_csv("Centralised decision maker Agent.csv")

                print(agent.name, "statistics: ")
                print("Nr of turns choosing: ", agent.nr_of_turns_choosing)
                print("Nr of turns waiting: ", agent.nr_of_turns_waiting)
                print("Nr of conflicts: ", agent.nr_of_conflicts)
                print("Nr of going to next order:", agent.nr_of_next_order)
                print("Total nr of moves: ", agent.total_nr_of_turns)
                print("")
