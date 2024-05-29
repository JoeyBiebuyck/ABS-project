#TODO add centralised agent
#TODO implement centralised agent
#TODO heel veel van de functies kunnen naar util verhuizen???
import grid_classes
import math
import util
import following_agent
class bigDogAgent(object):
    def __init__(self, grid, choosing_strategy, move_strategy):
        self.agents: list[following_agent.small_brain_agent] = []
        self.order: list[grid_classes.Product] = []
        self.available: list[grid_classes.Product] = [] # initieel gelijk aan de order
        self.choosing_strategy = choosing_strategy
        self.move_strategy = move_strategy
        self.grid = grid

    def assign_items(self, available_items, agents): # geeft alle agenten de items dat ze gaan moeten halen TODO: zet de agents_with_space als invoer idp van alle agents, zo kan je de conditional tak vermijden als je er geen hebt
        agents_with_space = filter(lambda agent: agent.chosen_items < agent.capacity, agents)
        while len(agents_with_space) != 0 or self.available != 0: # voor elke agent dat nog items kan kiezen
            for agent in agents_with_space:
                item = self.choosing_strategy(available_items) #TODO vraag: zijn we zeker dat de items niet dubbel gekozen worden? Dit zou moeten inorde zijn, grtjs os
                agent.add_item_to_chosen(item)

    def assign_move(self, agents):
        agents_with_items = filter(lambda agent: len(agent.chosen_items) != 0, agents)
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

    def distance_to_item_score(self, distance):
        if distance == 0:
            return 100
        else:
            return max (0, 50 - distance)

    def distance_to_item(self, position, list_of_items):
        list_of_positions = zip(list_of_items, map(lambda item_pos: self.euclidean_distance(item_pos, position), map(lambda item: self.grid.items_to_pos_dict[item], list_of_items)))
        nearest_item, distance_to_item = min(list_of_positions, key=lambda tuple: tuple[1])
        return nearest_item, distance_to_item

    def evaluate_move (self, agent, move): #TODO:  op basis van afstand naar een item
        score_move = 0
        x,y = agent.current_position
        new_position_agent = move
        nearest_item, distance_to_item = self.distance_to_item(new_position_agent, agent.chosen_items)

        score_move += distance_to_item
        return score_move