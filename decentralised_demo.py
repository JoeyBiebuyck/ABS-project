import threading

import decentralised_agent
import globals
import strategies
import util
import grid_classes
import logic_grid
import test_items

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

#TODO standaard testen maken voor de onderzoeksvraag
#TODO counter voor de efficientie

def play_and_show_grid():
    play_thread = threading.Thread(target=main_grid.play)
    play_thread.start()

def glob():
   global order_number
   order_number = 0

def joey_loop (lijst_van_paren):
    # maak de initiele files
    grid_size = 5
    util.init_stat_files(["Agent 0", "Agent 1"], decentralised=True)
    for order, item_dict in lijst_van_paren:
        new_grid = logic_grid.Decentralised_grid(item_dict, grid_size, strategy=strategies.strategy_1, nr_of_agents=2)
        new_grid.broadcast_order(order)
        new_grid.play()

if __name__ == "__main__":

    # grid_size = 5
    # items = ["apple", "peach", "banana", "strawberry", "watermelon", "orange"]
    # producten_lijst = [grid_classes.Product(items[i]) for i in range(6)]
    #
    # item_dict = util.build_dictionary(producten_lijst, grid_size)
    # #  vb_pos_lijst = [(0, 1), (2, 4), (2, 0), (2, 2), (1, 3), (2, 3)]
    # #  vb_item_dict = {}
    # #  for pos, item in zip(vb_pos_lijst, producten_lijst):
    # #      vb_item_dict[item] = pos
    # order = util.generate_order(producten_lijst, unique=True)
    # main_grid = logic_grid.Decentralised_grid(item_dict, grid_size, strategy=strategies.strat_k_means, nr_of_agents=2)
    # main_grid.broadcast_order(order)
    #
    #
    # # for loop dat
    #
    # # dit commenten om dan de grid gui uit te schakelen
    # #play_grid_thread = threading.Thread(target=play_and_show_grid)
    # #play_grid_thread.start()
    #
    # # ditook er bij zetten om play te doen
    #
    # main_grid.play()
    #
    # # main_grid.grid_ui.mainloop()
    #
    # # result_2_rfr_df = pd.DataFrame(data=pred_test_set, columns=["active_power"])
    # # result_2_rfr_df.reset_index(inplace=True)
    # # result_2_rfr_df = result_rfr_df.rename(columns={'index': 'id'})
    # # # kijken of het het juiste formaat is
    # # result_2_rfr_df.head()
    # # # %%
    # # result_2_rfr_df.to_csv('predictions_3_rfr.csv', index=False)

    test_items.init_orders()
    joey_loop(globals.orders_and_dicts)

