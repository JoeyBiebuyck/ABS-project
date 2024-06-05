import math
from utilities import util
from grids import logic_grid, grid_classes


class Decentralised_agent(object):
    def __init__(self, grid, strategy, name, capacity=2):
        self.starting_position: (int, int) = ...  # startpositie van de agent, is dezelfde locatie als het laadplatform, filler start positie
        self.current_position: (int, int) = ...  # huidige positie van de agent, filler initiele positie
        self.other_agents: list[Decentralised_agent] = []  # lijst van pointers naar de andere agenten
        self.capacity = capacity  # de grootte van de opslagcapaciteit van de agent
        self.storage = []  # wat er al in de opslagruimte zit
        self.strategy = strategy  # welke strategie gebruikt wordt om het volgende item te selecteren
        self.grid: logic_grid.Decentralised_grid = grid  # het logic grid
        self.chosen_items: list[(grid_classes.Product, int)] = []  # items die agent zelf gekozen heeft ("gereserveerd")
        self.selected_item = False  # het item waar de agent momenteel naartoe gaat
        self.highest_order = 0
        self.current_order = 0
        self.original_orders = {}  # dictionary van order number → originele order
        self.developing_orders = {}  # dictionary van order number → items van de order dat nog niet gedeposit zijn
        self.agent_choices = {}  # dictionary van order number → items dat andere agenten gekozen hebben van die bestelling
        self.available_items = {}  # dictionary van order number → items dat nog beschikbaar zijn van de bestelling
        self.name = "Agent " + str(name)

        # FOR TESTING:
        self.nr_of_turns_choosing = 0
        self.nr_of_turns_moving = 0
        self.nr_of_conflicts = 0
        self.nr_of_turns_depositing = 0
        self.nr_of_turns_picking_up = 0
        self.nr_of_turns_waiting = 0
        self.nr_of_next_order = 0
        self.total_nr_of_turns = 0

    # De methode die gebruikt wordt om te bepalen welke actie de agent neemt
    def play(self):
        self.total_nr_of_turns += 1
        available = self.available_items[self.current_order]
        print("Het is de beurt van: ", self.name)
        print("my choices: ", list(map(lambda product: product[0].name, self.chosen_items)))
        print("my storage: ", list(map(lambda product: product[0].name, self.storage)))
        print("other agent choices: ", list(map(lambda product: product.name, self.agent_choices[self.current_order])))
        print("current order: ", self.current_order)
        print("available items: ", list(map(lambda product: product.name, available)))
        print("developing items: ", list(map(lambda product: product.name, self.developing_orders[self.current_order])))

        if len(self.developing_orders[self.highest_order]) == 0:  # als de laatste order helemaal gedaan is, ben je klaar
            print("succes! all orders fulfilled\n")
            self.grid.stop()
        elif len(available) == 0 and self.current_order == self.highest_order and len(self.chosen_items) == 0 and len(self.storage) == 0:  # als de agent al zijn items gedeposit heeft, maar alle items al gereserveerd zijn, wacht tot de andere agenten hun items depositen
            self.nr_of_turns_waiting += 1
            print("cannot do anything else, he is waiting for the other agent to finish collecting items\n")
        elif self.capacity > len(self.chosen_items) and len(available) != 0 and len(self.storage) == 0:  # als je nog items kan "reserveren" van de huidige order, doe dat, storage == 0 check zodat je eerst alles deposit
            self.nr_of_turns_choosing += 1
            self.choose_item()
        elif self.highest_order > self.current_order and self.capacity > len(self.chosen_items) and len(available) == 0 and len(self.storage) == 0:  # als je items kan reserveren, maar de huidige available is leeg, ga naar next order
            self.nr_of_next_order += 1
            self.next_order()
        elif self.grid.has_item(self.current_position, list(map(lambda tuple: tuple[0], self.chosen_items))):  # als je op een positie bent waar een item is dat je gereserveerd hebt, raap het op
            self.nr_of_turns_picking_up += 1
            self.pick_up()
        elif self.grid.is_loading_dock(self.current_position, self) and len(self.storage) != 0:  # als je op je loading dock bent, deposit je items
            self.nr_of_turns_depositing += 1
            self.deposit()
        elif len(self.chosen_items) == 0:  # als je alle items hebt, keer terug naar huis
            print(self.name, "has retrieved all reserved items")
            self.nr_of_turns_moving += 1
            self.move(self.return_home())
        else:  # beweeg richting de items dat je gereserveerd hebt
            self.nr_of_turns_moving += 1
            self.move(self.select_next_product_and_position())  # we bepalen naar waar de agent moet bewegen.

    # Methode dat een item opraapt, oprapen gebeurt 1 item per keer
    # Kan uitgebreid worden zodat het item ook van de grid verdwijnt
    def pick_up(self):
        row, col = self.current_position
        item: grid_classes.Product = self.grid.logic_grid[row][col].item
        print("picking up :", item.name, "\n")
        order_nr = -1
        for tuple in self.chosen_items:  # omdat het een lijst van tuples is moet er geïtereerd worden over de lijst om het eerste element van de tuple te matchen, want we willen dat precies 1 tuple verwijderd wordt, niet meerdere
            product, order_number = tuple
            if product == item:
                order_nr = order_number
                self.chosen_items.remove(tuple)
                break
        self.storage.append((item, order_nr))
        self.selected_item = False
        for agent in self.other_agents:
            agent.agent_choices[order_nr].remove(item)

    # Methode dat een item deposit in het loading dock, depositen gebeurt 1 item per keer
    def deposit(self):
        row, col = self.current_position
        item, order_nr = self.storage.pop()
        print("depositing", item.name)
        loading_dock = self.grid.logic_grid[row][col].loading_dock
        loading_dock.contents.append(item)
        self.developing_orders[order_nr].remove(item)
        print("amount of items that need to be deposited for this order to be completed: ", len(self.developing_orders[order_nr]), "\n")
        for agent in self.other_agents:
            agent.developing_orders[order_nr].remove(item)

    # Methode dat een item kiest om te reserveren a.d.h.v. de strategie
    def choose_item(self):
        available = self.available_items[self.current_order]
        other_agent_choices = self.agent_choices[self.current_order]
        item = self.strategy(available, list(map(lambda tuple: tuple[0], self.chosen_items)), other_agent_choices, self.current_position, self.grid.items_to_pos_dict)  # verander hier de keuze methode
        self.available_items[self.current_order].remove(item)
        self.chosen_items.append((item, self.current_order))  # we slagen op van welk order het item dat we reserveren is, anders komen er problemen bij de overlap van 2 bestellingen (self.current_order komt dan niet helemaal overeen)
        print(item.name, "was chosen\n")
        for agent in self.other_agents:
            agent.agent_choices[self.current_order].append(item)  # zeg tegen andere agenten welk item je hebt gekozen
            agent.available_items[self.current_order].remove(item)

    # Methode dat de agent naar next_pos verplaatst, als een agent in de weg is wordt er uitgeweken (dat is een conflict)
    def move(self, next_pos):
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
            self.nr_of_conflicts += 1
        else:
            print("!!!error not adjacent!!!")

    # Methode dat een pad construeert en de beste positie geeft
    # returned de beste next position en roept de move methode op
    def select_next_product_and_position(self):
        print("selecting move")
        pos_chosen_items = []
        distance_to_available_items = []
        if not self.selected_item:  # als we nog geen item gekozen hebben om naartoe te gaan, kiezen we een nieuw dichtste item
            for item in list(map(lambda tuple: tuple[0], self.chosen_items)):  # gebruiken twee for loops om het dichtstbijzijnde object te kiezen.
                position_object = self.grid.items_to_pos_dict.get(item)
                pos_chosen_items.append(position_object)
            for pos in pos_chosen_items:
                distance_to_available_items.append(math.dist(self.current_position, pos))
            if len(distance_to_available_items) != 0:
                # selected_item is het item waar we naartoe willen gaan
                self.selected_item = self.chosen_items[(distance_to_available_items.index(min(distance_to_available_items)))][0]
        print("selected item: ", self.selected_item.name)

        # start and goal position for a star
        start = self.current_position
        goal = self.grid.items_to_pos_dict.get(self.selected_item)
        path = util.astar(self.grid, start, goal)
        # volgende positie die we willen bereiken.
        next_pos = self.current_position
        if path is not None:
            next_pos = path[0]
        print("current position is", self.current_position)
        print("next_pos: ", next_pos)
        print("path is: ", path, "\n")
        # move methode oproepen om naar de volgende positie te gaan
        return next_pos

    # Methode dat de positie teruggeeft waar de agent naartoe moet bewegen om naar zijn loading dock te gaan
    def return_home(self):
        print("returning home!!!")
        print("current returning position is: ", self.current_position)
        return_path = util.astar(self.grid, self.current_position, self.starting_position)
        next_pos = self.current_position
        if return_path is not None:
            next_pos = return_path[0]
        print("going to: ", next_pos, "\n")
        return next_pos

    # Methode dat de agent naar de volgende bestelling overschakelt
    def next_order(self):
        print(self.name, "is going to the next order")
        self.current_order += 1
        print("available items are:", list(map(lambda item: item.name, self.available_items[self.current_order])))
        print("other agent choices are:", list(map(lambda item: item.name, self.agent_choices[self.current_order])), "\n")