import threading
import strategies
import util
import grid_classes
import logic_grid


#TODO initialize voor de bigdog en smaalbrain agents
#TODO make it easy to switch between centralised and decentralised
#TODO standaard testen maken voor de onderzoeksvraag
#TODO counter voor de efficientie

def play_and_show_grid():
    play_thread = threading.Thread(target=main_grid.play)
    play_thread.start()


if __name__ == "__main__":
    grid_size = 5
    items = ["apple", "peach", "banana", "strawberry", "watermelon", "orange"]
    producten_lijst = [grid_classes.Product(items[i]) for i in range(6)]

    item_dict = util.build_dictionary(producten_lijst, grid_size)
    #  vb_pos_lijst = [(0, 1), (2, 4), (2, 0), (2, 2), (1, 3), (2, 3)]
    #  vb_item_dict = {}
    #  for pos, item in zip(vb_pos_lijst, producten_lijst):
    #      vb_item_dict[item] = pos
    order = util.generate_order(producten_lijst, unique=True)
    order2 = util.generate_order(producten_lijst, unique=True)
    main_grid = logic_grid.Decentralised_grid(item_dict, grid_size, strategy=strategies.strategy_1, nr_of_agents=2)
 #   main_grid.init_agents()  # als de init_agents() in de __init__ van de klasse maar 1 keer wordt opgeroepen, dan hoeft deze hier niet te staan
 #   main_grid.populate_grid()
    main_grid.broadcast_order(order)
    main_grid.broadcast_order(order2)

    play_grid_thread = threading.Thread(target=play_and_show_grid)
    play_grid_thread.start()

    main_grid.grid_ui.mainloop()
#  my_print(main_grid.logic_grid)
