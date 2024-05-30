#TODO add centralised agent
#TODO implement centralised agent
#TODO heel veel van de functies kunnen naar util verhuizen???
import grid_classes
import math
import util
import following_agent
class centralised_agent(object):
    def __init__(self, grid, following_agents, choosing_strategy, move_strategy, name):
        self.agents: list[following_agent.following_agent] = following_agents
        self.choosing_strategy = choosing_strategy
        self.move_strategy = move_strategy
        self.grid = grid
        self.current_order = 0
        self.highest_order = 0
        self.original_orders = {}  # dict van order number -> originele order
        self.developing_orders = {}  # dict van order number → items van de order dat nog niet gedeposit zijn
        self.agent_choices = {}  # dict van order number -> items dat andere agenten gekozen hebben van die bestelling
        self.available_items = {}  # dict van order number -> items dat nog beschikbaar zijn van de bestelling
        self.name = "Agent " + name

    def play(self):
        pass
    def assign_items(self, available_items, agents): # geeft alle agenten de items dat ze gaan moeten halen TODO: zet de agents_with_space als invoer idp van alle agents, zo kan je de conditional tak vermijden als je er geen hebt
        agents_with_space = filter(lambda agent: agent.appointed_items < agent.capacity, agents)
        available = self.available_items[self.current_order]
        while len(agents_with_space) != 0 or available != 0: # voor elke agent dat nog items kan kiezen
            for agent in agents_with_space:
                item = self.choosing_strategy(available_items)
                available.remove(item)
                agent.appointed_items += item

    def assign_move(self, agents): # geeft de beste move aan de agents
        agents_with_items = filter(lambda agent: len(agent.appointed_items) != 0, agents)
        for agent in agents_with_items:
            agent.move(self.calculate_best_move(agent))

    #valid moves zit in util.py
    #euclidian distance ook
    def calculate_best_move(self, agent): #TODO: Afhankelijk van de afstand naar item, 1kruisende paden, en borders.
        legal_moves = util.valid_moves(agent,self.grid)
        best_move = None
        best_score = 0
        for move in legal_moves:
            move_score = self.evaluate_move(agent, move)
            if move_score > best_score:
                best_score = move_score
                best_move = move
        return best_move

    def distance_to_item(self,position, list_of_items):
        list_of_positions = zip(list_of_items, map(lambda item_pos: math.dist(item_pos, position), map(lambda item: self.grid.items_to_pos_dict[item], list_of_items)))
        nearest_item, distance_to_item = min(list_of_positions, key=lambda tuple: tuple[1])
        return nearest_item, distance_to_item

    def evaluate_move (self, agent, move): #TODO: op basis van afstand naar een item
        score_move = 0
        x,y = agent.current_position
        new_position_agent = move
        nearest_item, distance_to_item = util.distance_to_item(new_position_agent, agent.chosen_items)
        score_move += util.distance_to_item_score(distance_to_item)
        return score_move