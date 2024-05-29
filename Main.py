from enum import Enum
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
import random
import math
import threading
import time
import util
import grid_classes
import decentralised_agent
import logic_grid

def initialize_grid(size, product_list):
    positions = util.build_dictionary(product_list, size)
    grid = logic_grid.Grid(positions, size)
    grid.populate_grid()
    return grid
def play_and_show_grid():
    play_thread = threading.Thread(target=main_grid.play)
    play_thread.start()
if __name__ == "__main__":
    grid_size = 5
    item1 = grid_classes.Product("item1")
    item2 = grid_classes.Product("item2")
    item3 = grid_classes.Product("item3")

    producten_lijst = [item1, item2, item3]
    item_dict = util.build_dictionary(producten_lijst, grid_size)
    order = util.generate_order(producten_lijst)
    main_grid = logic_grid.Grid(item_dict, grid_size)
    main_grid.init_agents()
    main_grid.populate_grid()
    main_grid.broadcast_order(order)

    play_grid_thread = threading.Thread(target=play_and_show_grid)
    play_grid_thread.start()

    main_grid.grid_ui.mainloop()
  #  my_print(main_grid.logic_grid)
