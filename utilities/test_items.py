from grids import grid_classes
import random
from utilities import globals, util

random.seed(1)


# Genereert 30 orders zodat bij OV1 de performantie berekent word voor dezelfde bestellingen en plaatsingen van items
def init_orders(grid_size=5, order_len=6, nr_of_examples=30):
    items = ["apple", "banana", "orange", "grapes", "strawberry", "watermelon", "pineapple", "mango", "kiwi", "pear",
             "cherry", "blueberry", "peach", "plum", "lemon", "lime", "avocado", "coconut", "pomegranate", "raspberry"]
    producten_lijst = [grid_classes.Product(items[i]) for i in range(order_len)]

    for _ in range(nr_of_examples):  # Voor elk voorbeeld
        coordinates = []
        while not len(coordinates) == len(items):  # Maak de coordinaten
            new_pos = util.generate_random_coordinate(0, grid_size - 2, 0,
                                                      grid_size - 1)  # onderste rij is gereserveerd voor load docks
            if new_pos not in coordinates:
                coordinates.append(new_pos)

        order = util.generate_order(producten_lijst, order_len, unique=True)
        item_to_pos_dict = {product: coordinates[i] for i, product in enumerate(producten_lijst)}  # bouw de dictionary
        globals.orders_and_dicts.append((order, item_to_pos_dict))  # Slaag ze op in globals

    for order, item_to_pos_dict in globals.orders_and_dicts:
        print("Order:", order)
        print("Item to Position Dictionary:", item_to_pos_dict)
        print()

    print(globals.orders_and_dicts)
