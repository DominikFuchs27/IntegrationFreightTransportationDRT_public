import Testing_Time
import GetMatrizes
import HelpingFunctions
import copy
import Testing_NewSchedule


def GreedyInsertion(Route):
    best_index_both_nodes = []
    Route.CalculateSchedule()
    Route.UpdateTimeWindows()  # Rearrange the order of "Route.time_earliest_departure_current" and "Route.time_latest_arrival_current" that it is in the same order as in the current sequence
    Route.UpdateSchedule(Route.schedule)  # Updates Route.schedule_origin and Route_schedule_destination that the value is the one of the current schedule
    denied_nodes, overall_waiting_time, new_schedule = Testing_Time.DepartureChecker(Route.GetCurrentOriginNodes(), Route.schedule_origin, Route.time_earliest_departure_current, Route)
    overall_distance = Route.OverallDistanceCalculator(Route.current_nodes)[0]
    old_cost = HelpingFunctions.CalculateCostInsertion(overall_distance,Route,denied_nodes,overall_waiting_time,new_schedule)           # Calculate the cost of the last current solution
    for m in range(len(Route.removed_nodes)):
        Route.OverallDistanceCalculator(Route.current_nodes)                 # Update the costlist that is only refers to the nodes, which are currently in use. Important for length of schedule!!
        costlist_testing = []                                                           # Create list for cost of each position, where node gets inserted --> retrieve the one with the lowest cost --> current (NOT OVERALL) best solution
        actual_position_dict = Route.actual_position                                    # Create dictionary with the actual positions of the nodes --> right sequence
        current_position_dict = Route.PositionCalculator(Route.current_nodes)           # Create dictionary with the current position in the sequence of the nodes
        index_removed_node = actual_position_dict.get(Route.removed_nodes[m])           # Get the index of the removed node --> know if origin or destination
        if index_removed_node % 2 == 0:  # Removed node is an origin
            OD_type = "Origin"
            name_trip_partner = list(actual_position_dict.keys())[list(actual_position_dict.values()).index(index_removed_node + 1)]    # Get the name of the partner-node (destination)
            index_current_partner = current_position_dict.get(name_trip_partner)    # Get index of the partner
            if index_current_partner is None:
                index_current_partner = len(Route.current_nodes)                    # if partner node not in sequence --> index is last entry
            Route.UpdateTimeWindows()           # Update time windows
            time_earliest_dep = Route.time_earliest_departure_starting[int(round(index_removed_node / 2))]  # get the earliest departure of the removed node
            if int(Route.removed_nodes[m].split('.')[1]) >= 10000 or int(name_trip_partner.split('.')[1]) >= 10000:   # Check if removed node is a package
                time_window_dep = Testing_Time.CalculateTimewindowDeparturePackage(time_earliest_dep)       # node is a package
            else:
                time_window_dep = Testing_Time.CalculateTimewindowDeparturePackage(time_earliest_dep)       # node is not a package
            time_latest_dep = time_window_dep[1]  # get the latest departure of the removed node
            Route.CalculateSchedule()
            Route.UpdateTimeWindows()  # Rearrange the order of "Route.time_earliest_departure_current" and "Route.time_latest_arrival_current" that it is in the same order as in the current sequence
            Route.UpdateSchedule(Route.schedule)  # Updates Route.schedule_origin and Route_schedule_destination that the value is the one of the current schedule
            #denied_nodes, overall_waiting_time, new_schedule = Testing_Time.DepartureChecker(Route.GetCurrentOriginNodes(), Route.schedule_origin, Route.time_earliest_departure_current, Route)
            #Route.UpdateTimeWindows()
            #Route.UpdateSchedule(new_schedule)              # Calculate a "real" schedule (with referring to nececessary depart/arrival times and not just durations)
            denied_nodes, overall_waiting_time, Route = Testing_NewSchedule.CalculateScheduleNew(Route)   # Update the schedule
            index_time_latest = 0                           # Set as 0 if the node needs to be in the beginning of the route
            for k in range(index_current_partner-1, 0,-1):  # Go through the nodes backwards, starting from the corresponding destination
                if Route.schedule[k] < time_latest_dep:      # find index, where current schedule is earlier than the latest depature
                    index_time_latest = k + 1                # + 1 because it is inserted after that node
                    break # Get the index, where the removed node could still fit in the schedule
            index_time_earliest = 0
            for l in range(index_time_latest-1,0,-1):
                if Route.schedule[l] < time_earliest_dep:   # find index, where current schedule is earlier than the earliest departure
                    index_time_earliest = l + 1
                    break
            if index_time_earliest == 0:
                index_time_latest = 1
            inserting_area = range(index_time_earliest, index_time_latest + 1)  # Possible inserting area before the corresponding destination AND in still in time for departure
        else:  # Removed node is a destination
            OD_type = "Destination"
            name_trip_partner = list(actual_position_dict.keys())[list(actual_position_dict.values()).index(index_removed_node - 1)]  # Get name of the current partner
            index_current_partner = current_position_dict.get(name_trip_partner)     # Get index of current partner (origin)
            if index_current_partner is None:                                   # If partner origin not in current sequence
                index_current_partner = 0                                                              # Later need to add +1 that it is after current partner --> First -1 makes it possible to put node at position 0
            time_latest_arr = Route.time_latest_arrival_starting[int(index_removed_node / 2)]           # Retriee time for latest arrival --> need to round down because arrival is always
            if int(Route.removed_nodes[m].split('.')[1]) >= 10000 or int(name_trip_partner.split('.')[1]) >= 10000:     # Check if removed node is a package
                time_earliest_arr = Testing_Time.CalculateTimewindowArrivalPackage(time_latest_arr)[0]        # Removed node is a pakcage
            else:
                time_earliest_arr = Testing_Time.CalculateTimewindowArrival(time_latest_arr)[0]         # Removed node is a passenger
            Route.CalculateSchedule()
            Route.UpdateTimeWindows()  # Rearrange the order of "Route.time_earliest_departure_current" and "Route.time_latest_arrival_current" that it is in the same order as in the current sequence
            Route.UpdateSchedule(Route.schedule)  # Updates Route.schedule_origin and Route_schedule_destination that the value is the one of the current schedule
            denied_nodes, overall_waiting_time, Route = Testing_NewSchedule.CalculateScheduleNew(Route)     # Calculate current schedule
            index_time_latest = len(Route.current_nodes)-1          # Latest input for destination is the lastest index
            if index_current_partner == len(Route.current_nodes)-1:         # if resembling origin is current at last index --> destination can only be directly afterwards
                inserting_area = [len(Route.current_nodes),len(Route.current_nodes)+1]
            else:
                for k in range(len(Route.schedule)-1, index_current_partner, -1):
                    if Route.schedule[k] < time_latest_arr:
                        index_time_latest = k + 1 # Get the index, where the removed node could still fit in the schedule
                        break
                index_time_earliest = index_current_partner + 1
                for l in range(index_time_latest-1,index_current_partner,-1):
                    if Route.schedule[l] < time_earliest_arr:
                        index_time_earliest = l
                inserting_area = range(index_time_earliest, index_time_latest + 1) # Add + 1 because last entry of range not included
        inserted = False
        for i in inserting_area:
            nodes_testing = Route.current_nodes[0:len(Route.current_nodes)]
            if i > len(Route.current_nodes):            # add node after the currently last entry
                nodes_testing.append(Route.removed_nodes[m])
                Route.current_nodes.append(Route.removed_nodes[m])
            else:
                nodes_testing.insert(i,Route.removed_nodes[m])    # insert nodes in all possible positions and take the one with the lowest costs
                Route.current_nodes.insert(i, Route.removed_nodes[m]) #
            if len(nodes_testing) != len(nodes_testing):        # Just for testing highest demand at some other place
                print("not possible")
            else:
                overall_dist = 0
                new_distance = []
                for j in range(1, len(nodes_testing)):  # start at 1 : origin not changed = Starting Point of Route
                    distance_node = GetMatrizes.GetDistance(nodes_testing[j-1],nodes_testing[j])
                    overall_dist += distance_node
                    new_distance.append(distance_node)  # Calculate new distance between each nodes
                Route.SetCurrentCostlist(new_distance)  # Set the new distance as current distance
                Route.CalculateSchedule()
                Route.UpdateTimeWindows()  # Rearrange the order of "Route.time_earliest_departure_current" and "Route.time_latest_arrival_current" that it is in the same order as in the current sequence
                Route.UpdateSchedule(Route.schedule)  # Updates Route.schedule_origin and Route_schedule_destination that the value is the one of the current schedule
                denied_nodes, overall_waiting_time, Route = Testing_NewSchedule.CalculateScheduleNew(Route)
                not_inserted_nodes = denied_nodes[:]
                not_inserted_nodes.extend(Route.removed_nodes[m:])
                c = HelpingFunctions.CalculateCostInsertion(overall_dist,Route,not_inserted_nodes,overall_waiting_time, Route.schedule)
                # Calculate the cost
                costlist_testing.append(c)
                if c < Route.best_cost and Route.MaxCapacityEvaluator() < 9 and Route.MaxCapacityEvaluatorPackage() < 10:      # Check if the new sequence is better than before and demand < capacity
                    Route.best_cost = c
                    Route.best_nodes = nodes_testing[:]
                    Route.best_schedule = copy.copy(Route.schedule)
                    Route.best_denied = denied_nodes[:]
                    Route.best_denied.extend(Route.removed_nodes[m+1::])
                    Route.best_overall_waiting_time = overall_waiting_time
                    Route.best_demand_route = Route.demand_route[:]
                    inserted = True
                    best_index = copy.copy(i)
                # removing the current node again to insert it at another position
                if i >= len(Route.current_nodes) and len(Route.current_nodes) != 1:
                    del Route.current_nodes[i-1]
                elif len(Route.current_nodes) == 1:
                    del Route.current_nodes[0]
                else:
                    del Route.current_nodes[i]   # Delete the inserted node for the next run
        if inserted == True: # check if there was at least 1 solution, where the node was able to be inserted --> insert it at best position
            Route.current_nodes.insert(best_index, Route.removed_nodes[m])
            best_index_both_nodes.append(best_index)
    Route = HelpingFunctions.CheckNodes(Route)          # Adds not implemented nodes as best.nodes_denied
    Route.CalculateSchedule()
    Route.UpdateTimeWindows()  # Rearrange the order of "Route.time_earliest_departure_current" and "Route.time_latest_arrival_current" that it is in the same order as in the current sequence
    Route.UpdateSchedule(Route.schedule)  # Updates Route.schedule_origin and Route_schedule_destination that the value is the one of the current schedule
    denied_nodes, overall_waiting_time, Route = Testing_NewSchedule.CalculateScheduleNew(Route)   # Calculate new schedule
    overall_distance = Route.OverallDistanceCalculator(Route.current_nodes)[0]                  # Calculate the new overall distance
    new_cost = HelpingFunctions.CalculateCostInsertion(overall_distance,Route,denied_nodes,overall_waiting_time, Route.schedule)
    delta_cost = new_cost - old_cost            # Calculate the difference in cost from before to after inserting the removed node
    if Route.removed_nodes[0] in Route.best_nodes:
        Route.best_nodes.remove(Route.removed_nodes[0])
    if Route.removed_nodes[1] in Route.best_nodes:
        Route.best_nodes.remove(Route.removed_nodes[1])
    if Route.removed_nodes[0] in Route.current_nodes:
        Route.current_nodes.remove(Route.removed_nodes[0])
    if Route.removed_nodes[1] in Route.current_nodes:
        Route.current_nodes.remove(Route.removed_nodes[1])
    Route.starting_nodes.remove(Route.removed_nodes[0])
    Route.starting_nodes.remove(Route.removed_nodes[1])
    Route.removed_nodes = []
    return Route, best_index_both_nodes, delta_cost
