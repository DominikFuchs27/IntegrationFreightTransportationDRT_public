import random
import itertools
import Route
import HelpingFunctions
import ALNS_Sub_Parallel
from operator import itemgetter
import itertools
import copy
import Parameters

def ALNS_Recursion(route_list_input, demand_pass, demand_pack, time_window, mydict, unfitting_nodes, removed_nodelist):
    cost_driver = 0
    denied_nodes = []
    for i in range(len(route_list_input)):
        route_list_input[i].best_nodes = route_list_input[i].current_nodes[:]
        if route_list_input[i].best_nodes:
            cost_driver += Parameters.cost_driver
    random.shuffle(unfitting_nodes)
    unfitting_nodes = list(itertools.chain(*unfitting_nodes))                                               # unfitting nodes is currently tuple --> unpack it into list
    removed_nodelist.extend(unfitting_nodes)
    for k in range(int(len(removed_nodelist)/2)):
        removed_nodes = [removed_nodelist[k*2],removed_nodelist[k*2+1]]
        #print(removed_nodes)
        delta_distance_list = []
        best_index_node_list = []
        for i in range(len(route_list_input)):
            route_list_input[i].removed_nodes = []
            evaluated_route = route_list_input[i]
            additional_driver = 0
            if not evaluated_route.current_nodes:
                additional_driver = Parameters.cost_driver
            starting_nodes = evaluated_route.starting_nodes[:]
            starting_nodes.extend(removed_nodes)
            trip_ids = HelpingFunctions.GetTripId(starting_nodes)  # Get Trip_id of the starting nodes --> important for rearranging nodes and get demand and time_window
            starting_nodes = HelpingFunctions.GenerateTuple(starting_nodes)
            demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.GetDemandAndTimeWindow(demand_pass, demand_pack, time_window, trip_ids)  # Get the demand and time-window of the starting nodes
            starting_nodes, demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.RearrangeStartingNodes(starting_nodes, demand_pass_route, demand_pack_route, time_window_route,trip_ids)  # Rearrange starting nodes that 0 comes first, then 1 and so on --> fitting demand, time-windows
            route_testing = Route.route(starting_nodes, demand_pass_route, mydict, time_window_route, demand_pack_route)# Create new route
            route_testing.removed_nodes = removed_nodes[:]  # Add removed nodes (with unfitting + removed nodes) to class
            route_testing.UpdateCurrentRoute(evaluated_route.current_nodes)
            route_testing, best_index_node, delta_distance = ALNS_Sub_Parallel.GreedyInsertion(route_testing)
            delta_distance += additional_driver
            if len(best_index_node) != 2:
                delta_distance = 5000
            best_index_node_list.append(best_index_node)
            delta_distance_list.append(delta_distance)
        if not best_index_node_list:
            denied_nodes.append(removed_nodes)
            break
        index_minimum = min(enumerate(delta_distance_list), key=itemgetter(1))[0]
        best_fitting_route = route_list_input[index_minimum]
        if len(best_index_node_list[index_minimum]) < 2:
            denied_nodes.append(removed_nodes)
        else:
            best_fitting_route.current_nodes.insert(best_index_node_list[index_minimum][0],removed_nodes[0])
            best_fitting_route.current_nodes.insert(best_index_node_list[index_minimum][1],removed_nodes[1])
            old_starting_nodes = best_fitting_route.starting_nodes[:]
            old_starting_nodes.extend(removed_nodes)
            trip_ids = HelpingFunctions.GetTripId(old_starting_nodes)  # Get Trip_id of the starting nodes --> important for rearranging nodes and get demand and time_window
            new_starting_nodes = HelpingFunctions.GenerateTuple(old_starting_nodes)  # Generate Tuple of starting nodes --> needed for input of new class
            demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.GetDemandAndTimeWindow(demand_pass, demand_pack, time_window, trip_ids)
            new_starting_nodes, demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.RearrangeStartingNodes(new_starting_nodes, demand_pass_route, demand_pack_route, time_window_route, trip_ids)
            new_route = Route.route(new_starting_nodes, demand_pass_route, mydict, time_window_route, demand_pack_route)
            new_route.current_nodes = best_fitting_route.current_nodes[:]
            new_route.best_nodes = new_route.current_nodes[:]
            #new_route.best_nodes = best_fitting_route.best_nodes[:]
            #new_route.current_nodes = new_route.best_nodes[:]
            #if len(new_route.current_nodes) != len(new_route.demand_route):
            #    print("lol")
            new_route = HelpingFunctions.UpdateRoute(new_route)
            route_list_input[index_minimum] = copy.deepcopy(new_route)
    for i in range(len(route_list_input)):              # Update Route if it was not previosuly changed --> need to adapt time_earlist_dep, because nodes have been removed
        if len(route_list_input[i].current_nodes) == 0:
            route_list_input[i] = HelpingFunctions.ClearRoute(route_list_input[i])
        if len(route_list_input[i].demand_node_current) > len(route_list_input[i].current_nodes):
            storage_current_node = route_list_input[i].current_nodes[:]
            trip_ids = HelpingFunctions.GetTripId(route_list_input[i].starting_nodes)
            new_starting_nodes = HelpingFunctions.GenerateTuple(route_list_input[i].starting_nodes)  # Generate Tuple of starting nodes --> needed for input of new class
            demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.GetDemandAndTimeWindow(demand_pass, demand_pack, time_window, trip_ids)
            new_starting_nodes, demand_pass_route, demand_pack_route, time_window_route = HelpingFunctions.RearrangeStartingNodes(new_starting_nodes, demand_pass_route, demand_pack_route,time_window_route, trip_ids)
            new_route = Route.route(new_starting_nodes, demand_pass_route, mydict, time_window_route, demand_pack_route)
            new_route.current_nodes = storage_current_node[:]
            new_route.best_nodes = new_route.current_nodes[:]
            route_list_input[i] = HelpingFunctions.UpdateRoute(new_route)
    return route_list_input, denied_nodes

    """
        #route_list_input[index_minimum].current_nodes.insert(best_index_node_list[index_minimum][0],removed_nodes[0])
        #route_list_input[index_minimum].best_nodes.insert(best_index_node_list[index_minimum][0],removed_nodes[0])
        #route_list_input[index_minimum].current_nodes.insert(best_index_node_list[index_minimum][0], removed_nodes[1])
        #route_list_input[index_minimum].best_nodes.insert(best_index_node_list[index_minimum][0], removed_nodes[1])
        best_node_list = route_list_input[index_minimum].best_nodes[:]
        best_node_list.insert(best_index_node_list[index_minimum][0], removed_nodes[0])
        best_node_list.insert(best_index_node_list[index_minimum][1], removed_nodes[1])
        route_list_input[index_minimum].current_nodes = best_node_list
        route_list_input[index_minimum].best_nodes = best_node_list
        old_starting_nodes = copy.copy(route_list_input[index_minimum].starting_nodes)
        old_starting_nodes.extend(removed_nodes)
        trip_ids = HelpingFunctions.GetTripId(old_starting_nodes)  # Get Trip_id of the starting nodes --> important for rearranging nodes and get demand and time_window
        new_starting_nodes = HelpingFunctions.GenerateTuple(old_starting_nodes)  # Generate Tuple of starting nodes --> needed for input of new class
        demand_route, time_window_route = HelpingFunctions.GetDemandAndTimeWindow(demand, time_window,trip_ids)  # Get the demand and time-window of the starting nodes
        new_starting_nodes, demand_route, time_window_route = HelpingFunctions.RearrangeStartingNodes(new_starting_nodes, demand_route, time_window_route, trip_ids)
        route_accepted = Route.route(new_starting_nodes, demand_route, mydict, time_window_route)  # Create new Route of accepted nodes
        route_list_input[i] = HelpingFunctions.ImportBestAttributes(route_list_input[index_minimum], route_accepted)

        #route_accepted = Route.route(nodes_accepted, demand_list_accepted, mydict,time_window_list_accepted)  # Create new Route of accepted nodes
    return route_list_input
    """