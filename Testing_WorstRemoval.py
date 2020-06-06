import random
import itertools
import HelpingFunctions
import Parameters

def CalculateWaitingTimeRequest(schedule_dep,earliest_dep):
    waiting_time_list = []
    for i in range(len(schedule_dep)):
        waiting_time_list.append(schedule_dep[i] - earliest_dep[i])   # create a list of waiting - times
    return waiting_time_list

def CalculateDistanceRequest(route):
    overall_dist, distance_list = route.OverallDistanceCalculator(route.current_nodes)
    distance_list.insert(0, 0)      # add 0 at beginning. No distance at the start
    distance_per_request = []
    current_position_dict = route.current_position
    actual_position_dict = route.actual_position
    for i in range(len(route.current_nodes)):
        index = actual_position_dict.get(route.current_nodes[i])
        if index % 2 == 0:       # node is an origin
            destination_name = route.starting_nodes[index+1]   # name of the destination
            index_destination = current_position_dict.get(destination_name)   # index of the destination
            distance_per_request.append(distance_list[i]+distance_list[index_destination])
    return distance_per_request

def CalculateCostRequestbased(route):
    # Calculate the costs according to each request --> no driver or denied nodes
    in_vehicle_time = HelpingFunctions.CalculateInVehicleTime(route,route.best_schedule)
    waiting_time = CalculateWaitingTimeRequest(route.schedule_origin, route.time_earliest_departure_current)
    distance = CalculateDistanceRequest(route)
    cost_list = []
    for i in range(len(in_vehicle_time)):
        cost_list.append(Parameters.weighing_service * (in_vehicle_time[i] + 2 * waiting_time[i]) + Parameters.weighing_service * distance[i])
    return cost_list

def WorstRemoval(route_list, degree_of_deconstruction, nodelist):
    #Removes the link with the highest cost
    number_of_removed_nodes = round(len(nodelist) * degree_of_deconstruction)   # number of requests to be deleted
    costlist = []
    for i in range(len(route_list)):
        costlist.extend(CalculateCostRequestbased(route_list[i]))           # list with costs
    cost_list_sorted, nodelist_sorted = zip(*sorted(zip(costlist, nodelist),reverse=True))  # sort the costs
    nodelist_sorted = list(nodelist_sorted)
    removed_nodelist = []
    indexes = []
    degree_of_randomisation = 6
    while len(removed_nodelist) < number_of_removed_nodes:      # remove all the nodes one after another
        y = random.uniform(0, 1)
        removed_node = nodelist_sorted[round(y ** degree_of_randomisation)]
        removed_nodelist.append(removed_node)
        indexes.append(nodelist.index(removed_node))
        nodelist_sorted.remove(removed_node)
    return removed_nodelist, indexes
