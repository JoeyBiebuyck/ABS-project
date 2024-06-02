import threading
from utilities import strategies, util
from grids import logic_grid, grid_classes


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
    order2 = util.generate_order(producten_lijst, unique=True)
    main_grid = logic_grid.Centralised_grid(item_dict, grid_size, choose_strategy=strategies.strategy_1, move_strategy= util.astar, nr_of_agents=2)
    main_grid.init_agents()
    main_grid.populate_grid()
    main_grid.broadcast_order(order)
    main_grid.broadcast_order(order2)

    if visuals:
        play_grid_thread = threading.Thread(target=play_and_show_grid)
        play_grid_thread.start()
        main_grid.grid_ui.mainloop()
    else:
        main_grid.play()
