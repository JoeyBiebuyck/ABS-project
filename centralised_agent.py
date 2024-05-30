#TODO add centralised agent
#TODO implement centralised agent
#TODO heel veel van de functies kunnen naar util verhuizen???
import grid_classes
import math
import util
import following_agent
class centralised_agent(object):
    def __init__(self, grid, following_agents, choosing_strategy, move_strategy, name):
        self.working_agents: list[following_agent.following_agent] = following_agents
        self.choosing_strategy = choosing_strategy
        self.move_strategy = move_strategy
        self.grid = grid
        self.current_order = 0
        self.highest_order = 0
        self.original_orders = {}  # dict van order number -> originele order
        self.developing_orders = {}  # dict van order number → items van de order dat nog niet gedeposit zijn
        self.agent_choices = {}  # dict van order number -> items dat andere agenten gekozen hebben van die bestelling
        self.available_items = {}  # dict van order number -> items dat nog beschikbaar zijn van de bestelling
        self.name = "Agent " + str(name)

    def play(self):  # kies actie
        for agent in self.working_agents:
            available = self.available_items[self.current_order]
            print("Het is de beurt van: ", agent.name)
            print("current order: ", self.current_order)
            print("available items: ", list(map(lambda product: product.name, available)))
            print("developing items: ", list(map(lambda product: product.name, self.developing_orders[self.current_order])))
            if len(self.developing_orders[
                       self.highest_order]) == 0:  # als de laatste order helemaal gedaan is, ben je klaar
                print("succes! all orders fulfilled\n")
                self.grid.stop()
            elif len(available) == 0 and self.current_order == self.highest_order and len(self.chosen_items) == 0 and len(
                    self.storage) == 0:
                print("cannot do anything else, he is waiting for the other agent to finish collecting items\n")
            elif self.capacity > len(self.chosen_items) and len(available) != 0 and len(
                    self.storage) == 0:  # als je nog items kan "reserveren" van de huidige order, doe dat, storage == 0 check zodat je eerst alles deposit
                self.choose_item()
            elif self.highest_order > self.current_order and self.capacity > len(self.chosen_items) and len(
                    available) == 0 and len(
                    self.storage) == 0:  # als je items kan reserveren, maar de huidige available is leeg, ga naar next order en doe het opnieuw
                self.next_order()
            elif self.grid.has_item(self.current_position,
                                    self.chosen_items):  # als je op een positie bent waar een item is dat je nodig hebt, raap het op
                self.pick_up()
            elif self.grid.is_loading_dock(self.current_position, self) and len(
                    self.storage) != 0:  # als je op je loading dock bent, deposit je items
                self.deposit()
            elif len(self.chosen_items) == 0:  # als je alle items hebt keer terug naar huis
                print(self.name, "has retrieved all reserved items\n")
                self.move(self.return_home())
            else:
                self.move(self.select_next_product_and_position())  # we bepalen naar waar de agent moet bewegen.

    def assign_items(self, available_items, agents): # geeft alle agenten de items dat ze gaan moeten halen TODO: zet de agents_with_space als invoer idp van alle agents, zo kan je de conditional tak vermijden als je er geen hebt
        agents_with_space = filter(lambda agent: agent.appointed_items < agent.capacity, agents)
        available = self.available_items[self.current_order]
        while len(agents_with_space) != 0 or available != 0: # voor elke agent dat nog items kan kiezen
            for agent in agents_with_space:
                item = self.choosing_strategy(available_items)
                available.remove(item)
                agent.appointed_items += item
    def make_move(self, agent,next_pos):
        agent.move(next_pos)

    def make_pick_up(self, agent):
        agent.pickup()
    def make_deposit(self,agent):
        agent.pickup()

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

    def Find_closest_item(self,position, list_of_items): #zoekt het dichtste product en geeft de afstand weer
        list_of_positions = zip(list_of_items, map(lambda item_pos: math.dist(item_pos, position), map(lambda item: self.grid.items_to_pos_dict[item], list_of_items)))
        nearest_item, distance_to_item = min(list_of_positions, key=lambda tuple: tuple[1])
        return nearest_item, distance_to_item

    def evaluate_move (self, agent, move): #TODO: op basis van afstand naar een item
        score_move = 0
        x,y = agent.current_position
        new_position_agent = move
        nearest_item, distance_to_item = self.distance_to_item(new_position_agent, agent.chosen_items)
        score_move += util.distance_to_item_score(distance_to_item)
        return score_move