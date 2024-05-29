import numpy as np
import random
import math
import threading
import time
def strategy_1(available, chosen_items, other_agent_choices, current_position, product_locations_dictonairy):
    location_available_items = []
    distance_to_available_items = []
    for item in available:
        #print("item: ", item)
        location = product_locations_dictonairy.get(item)
        location_available_items.append(location)

    if len(other_agent_choices) == 0: #als er nog geen intentions zijn kiezen we het dichtste item
        for pos in location_available_items:
            #print("position: ", pos)
            distance_to_available_items.append(math.dist(pos, current_position))
            #print("return: ", available[(distance_to_available_items.index(min(distance_to_available_items)))])
        return available[(distance_to_available_items.index(min(distance_to_available_items)))]
    else:
        for i in location_available_items:
            #print("this is the location of an available item: ", i)
            #print("this is the other agent choice: ", other_agent_choices[-1])
            distance_to_available_items.append(math.dist(i, product_locations_dictonairy.get(other_agent_choices[-1])))
        return available[(distance_to_available_items.index(max(distance_to_available_items)))]