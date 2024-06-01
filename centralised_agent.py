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

        # FOR TESTING:
        self.nr_of_turns_choosing = 0
        self.nr_of_conflicts = 0
        self.nr_of_turns_waiting = 0
        self.nr_of_next_order = 0
        self.total_nr_of_turns = 0

    def play(self):  # kies actie
        for agent in self.working_agents:
            self.total_nr_of_turns += 1
            available = self.available_items[self.current_order]
            print("Het is de beurt van: ", agent.name)
            print("current order agent: ", agent.current_order)
            print("available items: ", list(map(lambda product: product.name, available)))
            print("appointed: ", list(map(lambda tuple: (tuple[0].name, tuple[1]), agent.appointed_items)))
            print("developing items: ")
            for k, v in self.developing_orders.items():
                                            print(k, list(map(lambda product: product.name,v)))

            if len(self.developing_orders[self.highest_order]) == 0:  # als de laatste order helemaal gedaan is, stop de grid
                print("succes! all orders fulfilled\n")
                self.grid.stop()

            elif len(self.developing_orders[self.current_order])==0: #als de huidige order voldaan is, ga naar de volgende
                self.nr_of_next_order += 1
                self.current_order = self.current_order + 1

            elif (len(available) == 0 and agent.current_order == self.highest_order and len(agent.appointed_items) == 0 #als toch alles leeg is moet je wachten op de andere agent
                 and len(agent.storage) == 0):
                self.nr_of_turns_waiting += 1
                print("cannot do anything else, he is waiting for the other agent to finish collecting items\n")

            elif (agent.capacity > len(agent.appointed_items) and len(available) != 0 and len(agent.storage) == 0):  # als je nog items kan "reserveren" van de huidige order, doe dat, storage == 0 check zodat je eerst alles deposit
                self.appoint_item(agent)

            elif self.highest_order > agent.current_order and agent.capacity > len(agent.appointed_items) and len(available) == 0 and len(agent.storage) == 0:  # als je items kan reserveren, maar de huidige available is leeg, ga naar next order en doe het opnieuw
                self.next_order(agent)

            elif self.grid.has_item(agent.current_position,list(map(lambda tuple: tuple[0], agent.appointed_items))):  # als je op een positie bent waar een item is dat je nodig hebt, raap het op
                self.make_pick_up(agent)

            elif self.grid.is_loading_dock(agent.current_position, agent) and len(agent.storage) != 0:  # als je op je loading dock bent, deposit je items
                self.make_deposit(agent)

            elif len(agent.appointed_items) == 0:  # als je alle items hebt keer terug naar huis
                print(agent.name, "has retrieved all appointed items\n")
                self.make_move(agent, self.find_way_home(agent))

            else:
                self.make_move(agent, self.select_next_product_and_position(agent))  # we bepalen naar waar de agent moet bewegen.

    def next_order(self, agent):
        print("going to the next order")
        print("available items are:", list(map(lambda item: item.name, self.available_items[agent.current_order])))
        print("other agent choices are:", list(map(lambda item: item.name, self.agent_choices[agent.current_order])),"\n")
        agent.current_order += 1

    def appoint_item(self, agent):#kiest item a.d.h.v. strategie en geeft het aan de agent
        available = self.available_items[self.current_order]
        other_agent_choices = []
        for other_agent in filter(lambda agent_in_working_agents: agent_in_working_agents != agent, self.working_agents):
            other_agent_choices += other_agent.appointed_items
        item = self.choosing_strategy(available, list(map(lambda tuple: tuple[0], agent.appointed_items)),  list(map(lambda tuple: tuple[0], other_agent_choices)), agent.current_position, self.grid.items_to_pos_dict)  # verander hier de keuze methode
        self.available_items[self.current_order].remove(item)
        agent.appointed_items.append((item, self.current_order))
        print(item.name, "was chosen\n")

    def make_move(self, agent, next_pos):
        next_pos_row, next_pos_col = next_pos
        if util.adjacent(agent.current_position, next_pos) and self.grid.logic_grid[next_pos_row][next_pos_col].agent is None:
            # als er geen agent is gaan we gwn naar de volgende positie
            agent.move(next_pos)
        elif util.adjacent(agent.current_position, next_pos):
            # als er een agent is wijken we uit naar rechts.
            self.nr_of_conflicts += 1
            alternative_position = util.move_right(agent.current_position, next_pos, self.grid.size)
            agent.move(alternative_position)
        else:
            print("!!!error not adjacent!!!")

    def make_pick_up(self, agent):
        agent.pick_up()

    def make_deposit(self,agent):
        item, order_nr = agent.deposit()
        print(" deposit item: ", item.name)
        print("order_nr deposit: ", order_nr)
        self.developing_orders[order_nr].remove(item)

    def find_way_home(self,agent):
        print("returning home!!!")
        print("current returning position is: ", agent.current_position)
        return_path = self.move_strategy(self.grid, agent.current_position, agent.starting_position)
        next_pos = return_path[0]
        print("going to: ", next_pos, "\n")
        return next_pos

    def select_next_product_and_position(self, agent):
        # construeert pad en geeft de beste next position weer
        # returns de beste next position en roept de move methode op.
        print("selecting move")
        pos_chosen_items = []
        distance_to_available_items = []
        appointed_items_without_order = list(map(lambda tuple: tuple[0], agent.appointed_items))
        if not agent.to_get_item:  # als we nog niet achter een item gaan , kiezen we een nieuw dichste item
            for item in appointed_items_without_order:  # gebruiken twee for loops om het dichtste object te kiezen.
                position_object = self.grid.items_to_pos_dict.get(item)
                pos_chosen_items.append(position_object)
            for pos in pos_chosen_items:
                distance_to_available_items.append(math.dist(agent.current_position, pos))
            if len(distance_to_available_items) != 0:
                # selected_item is het item waar we achter gaan
                agent.to_get_item = appointed_items_without_order[(distance_to_available_items.index(min(distance_to_available_items)))]
        print("selected item: ", agent.to_get_item.name)

        # start and goal position for a star
        start = agent.current_position
        goal = self.grid.items_to_pos_dict.get(agent.to_get_item)
        path = self.move_strategy(self.grid, start, goal)
        # volgende positie die we willen bereiken.
        next_pos = path[0]
        print("current position is", agent.current_position)
        print("next_pos: ", next_pos)
        print("path is: ", path, "\n")
        # move methode oproepen om naar de volgende positie te gaan
        return next_pos
