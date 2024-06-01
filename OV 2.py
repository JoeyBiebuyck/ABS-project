import util
import logic_grid
import globals
import strategies
import grid_classes
import pandas as pd

# welke maten kiezen we?
# aantal agenten: 1, 2, 3, 4
# aantal producten: 4, 8, 12, 16, 20
# grootte van de grid: 5, 8, 10, 20
# grootte van de bestelling: 4, 8, 12, 16
items = ["apple", "banana", "orange", "grapes", "strawberry", "watermelon", "pineapple", "mango", "kiwi", "pear",
         "cherry", "blueberry", "peach", "plum", "lemon", "lime", "avocado", "coconut", "pomegranate",
         "raspberry"]
producten_lijst = [grid_classes.Product(items[i]) for i in range(6)]

nr_of_agents = [1, 2, 3, 4]
nr_of_products = [4, 8, 12, 16, 20]
grid_size = [5, 8, 10, 20]
order_size = [4, 8, 12, 16]


def iteratie_loop():
    # maak de initiele files
    util.init_stat_files(["Agent 0", "Agent 1", "Agent 2", "Agent 3"], True)
    util.init_stat_files_OV2()
    for number_of_products in nr_of_products:
        lijst_producten = producten_lijst[:number_of_products]
        globals.nr_of_products = number_of_products
        for grootte_van_grid in grid_size:
            item_dict = util.build_dictionary(lijst_producten, grootte_van_grid)
            globals.grid_size = grootte_van_grid
            for grootte_van_bestelling in order_size:
                order = util.generate_order(lijst_producten, length_of_order=grootte_van_bestelling)
                globals.order_size = grootte_van_bestelling
                for number_of_agents in nr_of_agents:
                    globals.nr_of_agents = number_of_agents
                    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                    print("current global order number: ", globals.order_number)
                    globals.order_number += 1
                    new_grid = logic_grid.Decentralised_grid(item_dict, grootte_van_grid,
                                                             strategy=strategies.strategy_1,
                                                             nr_of_agents=number_of_agents, record_stats=True)
                    new_grid.broadcast_order(order)



                    new_grid.play()


if __name__ == "__main__":
    iteratie_loop()
