import math
from sklearn.cluster import KMeans
import random
import numpy as np

# Strategy 1 zal als er nog geen enkel item gereserveerd is, het dichtste item bij de agent terug geven.
# Als er al een item gereserveerd is door een andere agent dan nemen we het item het verst van dat item.
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
            #print("this is the other agent choice: ", agent_choices[-1])
            distance_to_available_items.append(math.dist(i, product_locations_dictonairy.get(other_agent_choices[-1])))
        return available[(distance_to_available_items.index(max(distance_to_available_items)))]



# deze strategie zal elke keer een willekeurig item geven. Deze strategie kan enkel gebruikt worden om te vergelijken
# aangezien alles willekeurig plaats vindt.

def strategy_2(available, chosen_items, other_agent_choices, current_position, product_locations_dictonairy):
    random_item = random.choice(available)
    return random_item

# strategie 3 zal dan elke keer het  dichtstbijzijnde item teruggeven.
def strategy_3(available, chosen_items, other_agent_choices, current_position, product_locations_dictonairy): #neemt altijd het dichtste item bij het eerder gekozen item
    items_distance = {}

    for item in available:
        item_location = product_locations_dictonairy.get(item)
        distance = math.dist(current_position, item_location)
        items_distance[item] = distance

    #sorteren op basis van de afstanden
    closest_item = min(items_distance, key=items_distance.get)

    return closest_item

# Deze strategie houdt rekening met de afstand tot andere agenten en afstancen tot de positie van items
# het zal een 30-70% gewicht geven aan deze twee aftsanden en die te proberen te balanceren
def strategy_balanced_proximity_avoidance(available, chosen_items, other_agent_choices, current_position,
                                          product_locations_dictionary):
    item_scores = {}
    #  als er geen andere agenten zijn met een intentie, kiezen we het dichtste item
    if len(other_agent_choices) == 0:
        return strategy_3(available, chosen_items, other_agent_choices, current_position,
                                     product_locations_dictionary)

    for item in available:
        item_location = product_locations_dictionary.get(item)
        # afstand van positie tot item
        distance_from_current = math.dist(current_position, item_location)
        # aftsand van de laatst gekozen item door ander agent
        other_agent_last_choice_location = product_locations_dictionary.get(other_agent_choices[-1])
        distance_from_other_agent_choice = math.dist(item_location, other_agent_last_choice_location)
        # we geven een score, combined score, op basis van hoe dicht en hoeveel agenten er mogelijks in de buurt zijn.
        combined_score = 0.7 * distance_from_current - 0.3 * distance_from_other_agent_choice
        item_scores[item] = combined_score
    # de beste score is de score die zo het laagste is.
    best_item = min(item_scores, key=item_scores.get)
    return best_item



# gebruik maken van k-means om te kiezen hoeveel clusters we maken van de items
# en we wijzen elke agent toe aan een cluster.
# Dus er worden clusters gemaakt van de available items en een agent wordt dan naar een cluster gestuurd.
# Ageten worden allemaal naar andere clusters gestuurd.
def strat_k_means(available, chosen_items, other_agent_choices, current_position, product_locations_dictionary):
    n_items = len(available)
    n_clusters = max(1, round(n_items / 3))
    item_locations = np.array([product_locations_dictionary[item] for item in available])
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(item_locations)
    labels = kmeans.labels_
    cluster_centers = kmeans.cluster_centers_

    current_cluster = labels[np.argmin([np.linalg.norm(current_position - center) for center in cluster_centers])]

    items_in_current_cluster = [item for item, label in zip(available, labels) if label == current_cluster]
    closest_item = min(items_in_current_cluster,
                       key=lambda item: np.linalg.norm(np.array(product_locations_dictionary[item]) - current_position))

    return closest_item
