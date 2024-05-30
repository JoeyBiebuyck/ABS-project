import math
import util
import grid_classes
import logic_grid
class Agent(object):
    def __init__(self, grid, strategy, name, capacity=2):
        self.starting_position: (int, int) = (-1, -1)  # is dezelfde locatie als het laadplatform, filler start positie
        self.current_position: (int, int) = (-1, -1)  # filler positie
        self.other_agents: list[Agent] = []  # lijst van pointers naar de andere agenten
        self.capacity = capacity  # storage van een agent
        self.storage = []  # wat zit er al in de storage
        self.strategy = strategy  # welke strategie op dit moment strat 1 is selected
        self.grid: logic_grid.Grid = grid  # logic grid
        self.available: list[grid_classes.Product] = []  # items van de order die nog niet gereserveerd zijn
        self.chosen_items: list[grid_classes.Product] = []  # items die agent zelf koos
        self.selected_item = False  # item dat de agent momenteel achter gaat
        self.other_agents_choices: list[grid_classes.Product] = []  # items die andere agents kozen
        self.highest_order = 0
        self.current_order = 0
        self.original_orders = {}  # dict van order number -> originele order
        self.developing_orders = {}  # dict van order number → items van de order dat nog niet gedeposit zijn
        self.name = "Agent " + str(name)

    def play(self):  # kies actie
        print("Het is de beurt van: ", self.name)
        print("current order: ", self.current_order)
        print("available items: ", list(map(lambda product: product.name, self.available)))
        print("developing items: ", list(map(lambda product: product.name, self.developing_orders[self.current_order])))
        if len(self.developing_orders[self.highest_order]) == 0:  # als de laatste order helemaal gedaan is, ben je klaar
            print("succes! all orders fulfilled")
            self.grid.stop()
        elif len(self.available) == 0 and self.current_order == self.highest_order and len(self.chosen_items) == 0 and len(self.storage) == 0:
            print("cannot do anything else, he is waiting for the other agent to finish collecting items")
        elif self.capacity > len(self.chosen_items) and len(self.available) != 0 and len(
            self.storage) == 0:  # als je nog items kan "reserveren" van de huidige order, doe dat, storage == 0 check zodat je eerst alles deposit
            self.choose_item()
        elif self.highest_order > self.current_order and self.capacity > len(self.chosen_items) and len(self.available) == 0 and len(self.storage) == 0:  # als je items kan reserveren, maar de huidige available is leeg, ga naar next order en doe het opnieuw
            self.next_order()
        elif self.grid.has_item(self.current_position, self.chosen_items):  # als je op een positie bent waar een item is dat je nodig hebt, raap het op
            self.pick_up()
        elif self.grid.is_loading_dock(self.current_position, self) and len(self.storage) != 0:  # als je op je loading dock bent, deposit je items
            self.deposit()
        elif len(self.chosen_items) == 0:  # als je alle items hebt keer terug naar huis
            print(self.name, "has retrieved all orders")
            self.move(self.return_home())
        else:
            self.move(self.select_next_product_and_position())  # we bepalen naar waar de agent moet bewegen.

    def pick_up(self): #raapt een item op #TODO remove from grid?
        row, col = self.current_position
        item: grid_classes.Product = self.grid.logic_grid[row][col].item
        self.chosen_items.remove(item)
        self.storage.append(item)
        self.selected_item = False
        print("picking up :", item.name, "\n")

    def deposit(self):  # geeft item af aan een loading dock
        row, col = self.current_position
        item = self.storage.pop()
        print("depositing", item.name)
        loading_dock = self.grid.logic_grid[row][col].loading_dock
        loading_dock.contents.append(item)
        print("amount of items that need to be deposited for this order to be completed: ", len(self.developing_orders[self.current_order]), "\n")
        self.developing_orders[self.current_order].remove(item)

        for agent in self.other_agents:
            agent.developing_orders[self.current_order].remove(item)

        # if len(curr_to_deposit) == 0: # laat iedereen naar het volgende order gaan als de andere compleet is TODO: laten we ze misschien al items van andere bestellingen verzamelen?
        #     self.next_order()
        #     # for agent in self.other_agents: #kan misschien zonder deze, anders moet het met, alleen als we errors krijgen tho
        #     #     agent.next_order()

    def choose_item(self):  # kiest een item a.d.h.v de strategie.
        item = self.strategy(self.available, self.chosen_items, self.other_agents_choices, self.current_position, self.grid.items_to_pos_dict)  # verander hier de keuze methode
        self.available.remove(item)
        self.chosen_items.append(item)
        for agent in self.other_agents:
            agent.available.remove(item)
            agent.other_agents_choices.append(item)

    def move(self, next_pos):  # beweegt de agent naar next_pos, wijkt uit voor andere agenten.#TODO is move right nog nodig als astar deftig werkt?
        curr_pos_row, curr_pos_col = self.current_position
        next_pos_row, next_pos_col = next_pos
        if util.adjacent(self.current_position, next_pos) and self.grid.logic_grid[next_pos_row][next_pos_col].agent is None:
            # als er geen agent is gaan we gwn naar de volgende positie
            if not util.out_of_bounds(next_pos, self.grid.size):
                self.grid.logic_grid[curr_pos_row][curr_pos_col].agent = None
                self.grid.logic_grid[next_pos_row][next_pos_col].agent = self
                self.current_position = next_pos
            else:
                print("!!!!!error next_post out of bounds!!!!!")
        elif util.adjacent(self.current_position, next_pos):
            # als er een agent is wijken we uit naar rechts.
            alternative_position = util.move_right(self.current_position, next_pos, self.grid.size)
            alt_next_pos_row, alt_next_pos_col = alternative_position
            self.grid.logic_grid[curr_pos_row][curr_pos_col].agent = None
            self.grid.logic_grid[alt_next_pos_row][alt_next_pos_col].agent = self
            self.current_position = alternative_position
        else:
            print("!!!error not adjacent!!!")

    def select_next_product_and_position(self): #TODO is het altijd het beste om eerst naar het dichste product te gaan?
        #construeert pad en geeft de beste next position weer
        #returns de beste next position en roept de move methode op.
        print("selecting move")
        pos_chosen_items = []
        distance_to_available_items = []
        if not self.selected_item:  # als we nog niet achter een item gaan , kiezen we een nieuw dichste item
            for item in self.chosen_items: #gebruiken twee for loops om het dichtste object te kiezen.
                position_object = self.grid.items_to_pos_dict.get(item)
                pos_chosen_items.append(position_object)
            for pos in pos_chosen_items:
                distance_to_available_items.append(math.dist(self.current_position, pos))
            if len(distance_to_available_items) != 0:
                #selected_item is het item waar we achter gaan
                self.selected_item = self.chosen_items[(distance_to_available_items.index(min(distance_to_available_items)))]
        print("selected item: ", self.selected_item.name)

        # start and goal position for a star
        start = self.current_position
        goal = self.grid.items_to_pos_dict.get(self.selected_item)
        path = util.astar(self.grid, start, goal)
        # volgende positie die we willen bereiken.
        next_pos = path[0]
        print("current position is", self.current_position)
        print("next_pos: ", next_pos)
        print("path is: ", path, "\n")
        # move methode oproepen om naar de volgende positie te gaan
        return next_pos

    def return_home(self):
        print("returning home!!!")
        print("current returning position is: ", self.current_position)
        return_path = util.astar(self.grid, self.current_position, self.starting_position)
        next_pos = return_path[0]
        print("going to: ", next_pos, "\n")
        return next_pos

    def next_order(self):
        print(self.name, "is going to the next order", "\n")
        self.current_order += 1
        self.available = self.developing_orders[self.current_order].copy()