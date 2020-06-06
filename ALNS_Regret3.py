import HelpingFunctions
import random
import itertools
from operator import itemgetter
import ALNS_Sub_Parallel
import copy
import Route
import heapq
import Parameters

def CalculateRegretValue(route_list_input,removed_nodes, demand_pass, demand_pack, time_window, mydict):
    # Calculates the regret value of the nodes
    denied_nodes = []
    delta_cost_list = []
    best_index_node_list = []
    for i in range(len(route_list_input)):
        route_list_input[i].removed_nodes = []
        evaluated_route = route_list_input[i]
        additional_driver = Parameters.cost_driver
        if not evaluated_route.current_nodes: # Cost of Driver
            additional_driver = Parameters.cost_driver
        starting_nodes = evaluated_route.starting_nodes[:]
        starting_nodes.extend(removed_nodes)
        trip_ids = HelpingFunctions.GetTripId(starting_nodes)  # Get Trip_id of the starting nodes --> important for rearranging nodes and get demand and time_window
        starting_nodes = HelpingFunctions.GenerateTuple(starting_nodes) # Generate Tuple of starting nodes --> needed for input of new class
        demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.GetDemandAndTimeWindow(demand_pass,demand_pack,time_window,trip_ids)  # Get the demand and time-window of the starting nodes
        starting_nodes, demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.RearrangeStartingNodes(starting_nodes, demand_pass_route, demand_pack_route, time_window_route,trip_ids)  # Rearrange starting nodes that 0 comes first, then 1 and so on --> fitting demand, time-windows
        route_testing = Route.route(starting_nodes, demand_pass_route, mydict, time_window_route, demand_pack_route)
        route_testing.removed_nodes = removed_nodes[:]  # Add removed nodes (with unfitting + removed nodes) to class
        route_testing.UpdateCurrentRoute(evaluated_route.current_nodes) # new route gets the same current nodes as the previous one
        route_testing, best_index_node, delta_cost = ALNS_Sub_Parallel.GreedyInsertion(route_testing)
        delta_cost += additional_driver
        if len(best_index_node) != 2:
            delta_cost = 5000
        best_index_node_list.append(best_index_node)   # saves, where the best index for the nodes was
        delta_cost_list.append(delta_cost)             # saves the increase in costs because of the insertion
    if not best_index_node_list:    # if no possible solution found --> node is denied
        denied_nodes.append(removed_nodes)
        print("Denied nodes:" + str(denied_nodes))
    index_best_route = min(enumerate(delta_cost_list), key=itemgetter(1))[0]   # index of least increase in cost
    index_insertion_nodes = best_index_node_list[index_best_route]
    index_third_best_route = int(heapq.nsmallest(4,enumerate(delta_cost_list),key=itemgetter(1))[2][0]) # index of third to least increase
    regret_value = delta_cost_list[index_third_best_route] - delta_cost_list[index_best_route]   # calculates regret value
    return index_best_route, regret_value, index_insertion_nodes, denied_nodes



def RegretHeuristic(route_list_input, demand_pass, demand_pack, time_window, mydict, unfitting_nodes, removed_nodelist):
    cost_driver = 0
    denied_nodes = []
    for i in range(len(route_list_input)):
        route_list_input[i].best_nodes = route_list_input[i].current_nodes[:]
        if route_list_input[i].best_nodes:
            cost_driver += Parameters.cost_driver
    random.shuffle(unfitting_nodes)                                         # randomly shuffle the unfitting nodes
    unfitting_nodes = list(itertools.chain(*unfitting_nodes))            # unfitting nodes is currently tuple --> unpack it into list
    removed_nodelist.extend(unfitting_nodes)
    while removed_nodelist:
        regret_value_list = []
        index_best_route_list = []
        index_best_insertion_nodes_list = []
        for k in range(int(len(removed_nodelist)/2)):
            removed_nodes = [removed_nodelist[k*2],removed_nodelist[k*2+1]]          # get through all removed nodes
            index_best_route, regret_value, index_insertion_nodes, denied_nodes_outcome = CalculateRegretValue(route_list_input, removed_nodes,  demand_pass, demand_pack, time_window, mydict)
            index_best_route_list.append(index_best_route)
            regret_value_list.append(regret_value)
            index_best_insertion_nodes_list.append(index_insertion_nodes)
        index_regret_maximum = max(enumerate(regret_value_list), key=itemgetter(1))[0]
        removed_nodes = [removed_nodelist[index_regret_maximum*2],removed_nodelist[index_regret_maximum*2+1]]
        index_overall_best_route = index_best_route_list[index_regret_maximum]
        best_fitting_route = route_list_input[index_overall_best_route]
        if len(index_best_insertion_nodes_list[index_regret_maximum]) < 2:
            denied_nodes.append(removed_nodes)
        else:
            best_fitting_route.current_nodes.insert(index_best_insertion_nodes_list[index_regret_maximum][0],removed_nodes[0]) # insert removed nodes at position with highest regret value
            best_fitting_route.current_nodes.insert(index_best_insertion_nodes_list[index_regret_maximum][1],removed_nodes[1])
            old_starting_nodes = best_fitting_route.starting_nodes[:]   # find the old strating nodes
            old_starting_nodes.extend(removed_nodes)
            trip_ids = HelpingFunctions.GetTripId(old_starting_nodes)  # Get Trip_id of the starting nodes --> important for rearranging nodes and get demand and time_window
            new_starting_nodes = HelpingFunctions.GenerateTuple(old_starting_nodes)  # Generate Tuple of starting nodes --> needed for input of new class
            demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.GetDemandAndTimeWindow(demand_pass, demand_pack, time_window, trip_ids)
            new_starting_nodes, demand_pack_route, demand_pass_route, time_window_route = HelpingFunctions.RearrangeStartingNodes(new_starting_nodes, demand_pass_route, demand_pack_route, time_window_route, trip_ids)
            new_route = Route.route(new_starting_nodes, demand_pass_route, mydict, time_window_route, demand_pack_route)
            new_route.current_nodes = best_fitting_route.current_nodes[:]    # overwrite the current nodes of the new route with the previously calculated current nodes
            new_route.best_nodes = new_route.current_nodes[:]
            new_route = HelpingFunctions.UpdateRoute(new_route)   # update the values of the new route with the ones of the old route
            route_list_input[index_overall_best_route] = copy.deepcopy(new_route)
        removed_nodelist.remove(removed_nodes[0])
        removed_nodelist.remove(removed_nodes[1])
        for i in range(len(route_list_input)):              # Update Route if it was not previosuly changed --> need to adapt time_earlist_dep, because nodes have been removed
            if len(route_list_input[i].current_nodes) == 0:
                route_list_input[i] = HelpingFunctions.ClearRoute(route_list_input[i])
            if len(route_list_input[i].demand_node_current) > len(route_list_input[i].current_nodes):
                storage_current_node = route_list_input[i].current_nodes[:]
                trip_ids = HelpingFunctions.GetTripId(route_list_input[i].starting_nodes)       # Get Trip IDs
                new_starting_nodes = HelpingFunctions.GenerateTuple(route_list_input[i].starting_nodes)  # Generate Tuple of starting nodes --> needed for input of new class
                demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.GetDemandAndTimeWindow(demand_pass, demand_pack, time_window, trip_ids)
                new_starting_nodes, demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.RearrangeStartingNodes(new_starting_nodes, demand_pass_route, demand_pack_route, time_window_route, trip_ids)
                new_route = Route.route(new_starting_nodes, demand_pass_route, mydict, time_window_route, demand_pack_route)
                new_route.current_nodes = storage_current_node[:]
                new_route.best_nodes = new_route.current_nodes[:]
                route_list_input[i] = HelpingFunctions.UpdateRoute(new_route)
    return route_list_input, denied_nodes
