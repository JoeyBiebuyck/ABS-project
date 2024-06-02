import threading
from utilities import strategies, util
from grids import logic_grid, grid_classes
from utilities import strategies, util
from grids import grid_classes, logic_grid


def play_and_show_grid():
    play_thread = threading.Thread(target=main_grid.play)
    play_thread.start()


if __name__ == "__main__":
    visuals = True
    grid_size = 5
    items = ["apple", "peach", "banana", "strawberry", "watermelon", "orange"]
    producten_lijst = [grid_classes.Product(items[i]) for i in range(6)]

    item_dict = util.build_dictionary(producten_lijst, grid_size)

    order = util.generate_order(producten_lijst, unique=True)
    main_grid = logic_grid.Decentralised_grid(item_dict, grid_size, strategy=strategies.strat_k_means, nr_of_agents=2)
    main_grid.broadcast_order(order)

    if visuals:
        # dit commenten om dan de grid gui uit te schakelen
        play_grid_thread = threading.Thread(target=play_and_show_grid)
        play_grid_thread.start()
        main_grid.grid_ui.mainloop()
    else:
        main_grid.play()

