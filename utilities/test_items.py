from utilities import util
from grids import grid_classes
import random
from utilities import globals

random.seed(1)


# TODO: maak (om te beginnen) 5 item_to_pos_dict en orders (in tuples)
def init_orders():
    items = ["apple", "peach", "banana", "strawberry", "watermelon", "orange"]
    producten_lijst = [grid_classes.Product(items[i]) for i in range(6)]

    nr_of_examples = 5
    grid_size = 5
    order_len = 6


    for _ in range(nr_of_examples):
        coordinates = [util.generate_random_coordinate(0, grid_size - 2, 0, grid_size - 1) for _ in range(order_len)]
        # order = [(producten_lijst[i], coordinates[i]) for i in range(order_len)]
        order = util.generate_order(producten_lijst, order_len, unique=True)
        item_to_pos_dict = {product: coordinates[i] for i, product in enumerate(producten_lijst)}
        globals.orders_and_dicts.append((order, item_to_pos_dict))

    for order, item_to_pos_dict in globals.orders_and_dicts:
        print("Order:", order)
        print("Item to Position Dictionary:", item_to_pos_dict)
        print()

    print(globals.orders_and_dicts)


# lijst van tuples met als eerste item een order en tweede een item to position dictionary

# item_dict = util.build_dictionary(producten_lijst, grid_size)
#  vb_pos_lijst = [(0, 1), (2, 4), (2, 0), (2, 2), (1, 3), (2, 3)]
#  vb_item_dict = {}
#  for pos, item in zip(vb_pos_lijst, producten_lijst):
#      vb_item_dict[item] = pos


