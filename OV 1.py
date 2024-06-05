from utilities import globals, strategies, util, test_items
from grids import logic_grid


# OV1: Is het mogelijk om het probleem op een gedecentraliseerde manier efficienter op te lossen dan op een gecentraliseerde manier?

# Loop die gebruikt werd om data te verzamelen voor de eerste onderzoeksvraag
# Om deze te gebruiken moet het visual grid uitgeschakeld worden
def iteratie_loop(lijst_van_paren, decentralised):
    # maak de initiele files
    grid_size = 5
    util.init_stat_files(["Agent 0", "Agent 1"], decentralised)  # Initieer files om de informatie van agenten op te slagen
    if decentralised:
        for order, item_dict in lijst_van_paren:  # voor elke order en plaatsing van items, genereer een grid en speel het af
            print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            globals.order_number += 1
            print("current global order number: ", globals.order_number)
            new_grid = logic_grid.Decentralised_grid(item_dict, grid_size, strategy=strategies.strat_k_means, nr_of_agents=2, record_stats=True)
            new_grid.broadcast_order(order)
            new_grid.play()
    else:
        for order, item_dict in lijst_van_paren:
            print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            globals.order_number += 1
            print("current global order number: ", globals.order_number)
            new_grid = logic_grid.Centralised_grid(item_dict, grid_size, choose_strategy=strategies.strat_k_means, nr_of_agents=2, record_strats=True)
            new_grid.broadcast_order(order)
            new_grid.play()


if __name__ == "__main__":
    test_items.init_orders()
    iteratie_loop(globals.orders_and_dicts, True)
    globals.order_number = 0
    iteratie_loop(globals.orders_and_dicts, False)
