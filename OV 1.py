import globals
import util
import logic_grid
import test_items
import strategies

## UNCOMMENT IN DE PLAY VAN DE GRIDS ZODAT DE VISUAL WERKT
def iteratie_loop(lijst_van_paren, decentralised):
    # maak de initiele files
    grid_size = 5
    util.init_stat_files(["Agent 0", "Agent 1"], decentralised)
    if decentralised:
        for order, item_dict in lijst_van_paren:
            print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            globals.order_number += 1
            print("current global order number: ", globals.order_number)
            new_grid = logic_grid.Decentralised_grid(item_dict, grid_size, strategy=strategies.strategy_1, nr_of_agents=2, record_stats=True)
            new_grid.broadcast_order(order)
            new_grid.play()
    else:
        for order, item_dict in lijst_van_paren:
            print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            globals.order_number += 1
            print("current global order number: ", globals.order_number)
            new_grid = logic_grid.Centralised_grid(item_dict, grid_size, choose_strategy=strategies.strategy_1, nr_of_agents=2, record_strats=True)
            new_grid.broadcast_order(order)
            new_grid.play()


if __name__ == "__main__":
    test_items.init_orders()
    iteratie_loop(globals.orders_and_dicts, True)
    globals.order_number = 0
    iteratie_loop(globals.orders_and_dicts, False)