import math
import random
import GetMatrizes

def CalculateRelatedeness(node, Route, node_index):
    Probability_factor = 5
    if node_index % 2 == 0:         # Origin
        node_origin = node
        pick_up_time = Route.time_earliest_departure_starting[int(node_index/2)]
        node_destination = list(Route.actual_position.keys())[list(Route.actual_position.values()).index(node_index + 1)]
        delivery_time = Route.time_latest_arrival_starting[int(node_index/2)]
    else:                           # Destination
        node_destination = node
        node_origin = list(Route.actual_position.keys())[list(Route.actual_position.values()).index(node_index - 1)]
        pick_up_time = Route.time_earliest_departure_starting[int((node_index - 1)/2)]
        delivery_time = Route.time_latest_arrival_starting[int((node_index - 1) / 2)]
        node_index += -1                # for range function later: Not comparing node with itself --> needs to be origin
    nodelist = Route.starting_nodes[:]
    relateness = []
    weighing_dist = 0.6
    weighing_time = 1
    nodelist_new = []
    for i in range(int(len(nodelist)/2)):    # go through all nodes
        if i*2 != node_index:
            delta_pickup_dist = (GetMatrizes.GetDistance(node_origin, nodelist[i*2]))/100               # pickup distance between requests
            delta_delivery_dist = (GetMatrizes.GetDistance(node_destination, nodelist[i*2+1]))/100      # delivery distance between requests
            delta_pickup_time = (pick_up_time - Route.time_earliest_departure_starting[i])/1000         # difference in pickup times between requests
            delta_delivery_time = (delivery_time - Route.time_latest_arrival_starting[i])/1000          # difference in delivery times between requests
            relateness.append(weighing_dist*(abs(delta_delivery_dist-delta_pickup_dist))+weighing_time*(abs(delta_pickup_time-delta_delivery_time))) # Calculate Relatedeness factor
            nodelist_new.append((nodelist[i*2],nodelist[i*2+1]))    # Store nodes
    relateness, nodelist_new = zip(*sorted(zip(relateness, nodelist_new)))   # sort nodelist and relateness
    r = random.uniform(0,1)
    retrieved_value = nodelist_new[int(r ** Probability_factor)]            # select the fitting requests
    return [node_origin, node_destination,retrieved_value[0],retrieved_value[1]]

def ShawRemoval(Mainroute, nodelist, degree_of_deconstruction):
    number_deleted_nodes = math.ceil(len(nodelist)*degree_of_deconstruction)   # calculate number of deleted nodes
    removed_nodes = []
    while len(removed_nodes) < number_deleted_nodes:
        index = random.randint(0,len(nodelist)-1)               # get random index
        node = Mainroute.starting_nodes[index]                  # find where it is in the original set
        if node not in removed_nodes:                           # only remove new nodes
            removed_nodes.extend(CalculateRelatedeness(node,Mainroute,index))
    indexes = []
    length = len(removed_nodes)
    i = 0
    while i < length:           # remove the nodes in the main route and store it in list
        if removed_nodes[i] in nodelist:
            indexes.append(nodelist.index(removed_nodes[i]))
            i += 1
        else:
            del removed_nodes[i]
            length -= 1
    return removed_nodes, indexes