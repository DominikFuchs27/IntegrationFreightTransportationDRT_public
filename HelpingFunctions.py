
import Parameters
import itertools
import Testing_NewSchedule

def GetTripId(nodelist):                # Retrieves the tripIds of a list of nodes
    trip_ids = []
    if isinstance(nodelist,list):
        for i in range(len(nodelist)):
            trip_ids.append(int(nodelist[i].split('.')[1]))
        trip_ids = list(dict.fromkeys(trip_ids))                            #Deletes Duplicates
        return trip_ids

def RearrangeStartingNodes(nodelist,demand_pass, demand_pack, time_windows,trip_ids):  # Sets a nodelist (and the belonging attributes) in the right order
    for i in range(len(trip_ids)):                              # Delete the additiona 10000 of the id of a package request
        if int(trip_ids[i]) >= 10000:
            trip_ids[i] = int(trip_ids[i]) - 10000
    ordered_nodelist = (max(trip_ids) + 1) * ['xx']             # Implement list with the length of the maximum trip id and 'xx' as placeholder
    ordered_demand_pass = (max(trip_ids) + 1) * ['xx']
    ordered_demand_pack = (max(trip_ids) + 1) * ['xx']
    ordered_time_windows = (max(trip_ids) + 1) * ['xx']
    for i in range(len(nodelist)):                                  # Set the values of nodelist/demand at the right position of the list
        ordered_nodelist[trip_ids[i]] = nodelist[i]                 # ['xx',('9876.1','9567.1'),'xx','xx']
        ordered_demand_pass[trip_ids[i]] = demand_pass[i]
        ordered_demand_pack[trip_ids[i]] = demand_pack[i]
        ordered_time_windows[trip_ids[i]] = time_windows[i]
    j = 0
    length = len(ordered_nodelist)
    while j < length:                                                   # Delete all placeholder "xx"
        if ordered_nodelist[j] == 'xx':
            ordered_nodelist.remove('xx')
            ordered_demand_pass.remove('xx')
            ordered_demand_pack.remove('xx')
            ordered_time_windows.remove('xx')
            length -= 1
        else:
            j += 1
    return ordered_nodelist, ordered_demand_pass, ordered_demand_pack, ordered_time_windows

def DeliveryGenerator(dict,input,tripID):                   # Generates a request between origin and destination adding the tripID
    start_index = input[0]
    end_index = input[1]                                                #index of the specific node for this trip in the dictionary
    start_name = str(input[0])+'.'+str(tripID)
    end_name = str(input[1]) + '.' + str(tripID)                        #Add the index of the trip to the nodename to have a unique key
    tripStart = dict[start_index]
    tripEnd = dict[end_index]
    trip = {start_name:dict[start_index],end_name:dict[end_index]}      #Dictionary with node name and coordinates for this trip
    return trip,tripStart,tripEnd

def PartnerFinder(denied_requests, Route):                      # Find the partner (either origin or destination) of a list
    actual_position_dict = Route.actual_position   # get the acutal positions
    nodes_denied = []
    trip_id_denied = []
    nodelist = Route.starting_nodes[:]
    nodes_checked = []
    for i in range(len(denied_requests)):                                           # Get tripID and partner of denied requests
        index_removed_node = actual_position_dict.get(denied_requests[i])           # Get the index of the node
        if index_removed_node == None:                                              # If the node is not in the route at all --> continue
            continue
        else:
            if index_removed_node % 2 == 0:          # Is ORIGIN
                name_trip_partner = list(actual_position_dict.keys())[list(actual_position_dict.values()).index(index_removed_node + 1)]  # Get name of the partner           # Get name of partner-destination --> the next node in the actual position sequence
                if any(name_trip_partner in s for s in nodes_checked) == False:         # Check if already been checked (e.g. a destination, which was previously checked as partner of an origin)
                    name_trip_partner_storage = name_trip_partner
                    nodes_checked.append(name_trip_partner)                 # add node to list of checked nodes
                    nodelist.remove(name_trip_partner)                      # remove node from nodelist
                    name_trip_origin = denied_requests[i]
                    nodes_checked.append(name_trip_origin)
                    nodelist.remove(name_trip_origin)
                    trip_id = name_trip_partner_storage.split('.')[1]              # Get the trip id                                                                             # Get trip id
                    trip_id_denied.append(int(trip_id))                             # List of trip ids
                    nodes_denied.append((name_trip_origin,name_trip_partner))       # List of all nodes, which have been collected
            if index_removed_node % 2 != 0:              # Is DESTINATION
                name_trip_partner = list(actual_position_dict.keys())[list(actual_position_dict.values()).index(index_removed_node - 1)]            # Get name of partner-origin --> the previous node in the actual position sequence
                name_trip_partner_storage = name_trip_partner
                if any(name_trip_partner in s for s in nodes_checked) == False:                 # Check if already been checked
                    nodes_checked.append(name_trip_partner)
                    nodelist.remove(name_trip_partner)                                          # Remove the node from the route
                    name_trip_destination = denied_requests[i]
                    nodes_checked.append(name_trip_destination)
                    nodelist.remove(name_trip_destination)
                    trip_id = name_trip_partner_storage.split('.')[1]                           # Get the trip id
                    trip_id_denied.append(int(trip_id))                                         # List of denied trip ids
                    nodes_denied.append((name_trip_partner, name_trip_destination))             # List of all nodes, which have been collected
    trip_id_accepted = [0] * (len(nodelist))
    for i in range(len(nodelist)):              # Create list for accepted nodes
            node = nodelist[i]
            trip_id_accepted[i] = int(node.split('.')[1])    # create list of trip_ids [2,2,5,5,...]
    nodes_accepted = []
    k = 1
    while k < len(nodelist):
        nodes_accepted.append((nodelist[k-1], nodelist[k]))    # create list of accepted nodes in the right order [('123.1','456.1'),('567.3',765.3')....]
        k += 2
    trip_id_accepted = list(dict.fromkeys(trip_id_accepted))   # removed duplicates of trip Ids
    nodes_denied = list(dict.fromkeys(nodes_denied))           # remove duplicates of denied nodes
    trip_id_denied = list(dict.fromkeys(trip_id_denied))       # remove duplicates of denied trip Ids
    return nodes_denied, trip_id_denied, nodes_accepted, trip_id_accepted


def GetDemandAndTimeWindow(demand_pass, demand_pack, time_window,trip_ids):  # Gets the demand and time-window of the inserted nodes, INPUT: Demand [2,3,1,1], time-window [(0,35),(10,45], trips_ids [2,6,3,5]
    for i in range(len(trip_ids)):             # check if request is a package
        if int(trip_ids[i]) >= 10000:
            trip_ids[i] = int(trip_ids[i]) - 10000
    demand_pass_list = [0] * len(trip_ids)
    demand_pack_list = [0] * len(trip_ids)
    time_window_list = [0] * len(trip_ids)
    for i in range(len(trip_ids)):
        trip = trip_ids[i]
        demand_pass_list[i] = demand_pass[trip]
        demand_pack_list[i] = demand_pack[trip]
        time_window_list[i] = time_window[trip]
    return demand_pass_list, demand_pack_list, time_window_list

def TwoNodeRoute(Route):         # creates fast solution of there are only 2 nodes in the route
    Route.best_cost = Route.current_overall_dist
    Route.time_previous_stop = Route.time_earliest_departure_starting[0]
    Route.schedule = Route.CalculateSchedule()
    Route.best_schedule = Route.schedule
    current_demand = Route.CreateCurrentDemand()
    Route.best_demand_route = Route.DemandSummation(current_demand)
    return Route

def GenerateTuple(nodelist):            # takes a list of nodes and generates a list with tuples
    output_nodelist = []
    for i in range(1,len(nodelist),2):
        output_nodelist.append((nodelist[i-1],nodelist[i]))
    return output_nodelist

def RemoveNodes(buslist,busdict,removed_nodes):                             # Takes a list with all routes, a dictionary with all routes and the previosly removed nodes. Output: Updated List with busses, with removed nodes as attributes and current nodes adapted
    fitted_list = []
    for i in range(len(removed_nodes)):
        fitted_list.append(busdict.get(removed_nodes[i]))        # Generate a list, in which bus all removed nodes are, e.g. [2,1,1,1,0,0,0]
    nodes_checked = []
    for i in range(len(removed_nodes)):
        if removed_nodes[i] not in nodes_checked:
            partner_node, trip_id_denied, nodes_accepted, trip_id_accepted = PartnerFinder([removed_nodes[i]], buslist[fitted_list[i]])
            buslist[fitted_list[i]].removed_nodes.append(partner_node[0][0])        # add the nodes to the removed nodes
            buslist[fitted_list[i]].current_nodes.remove(partner_node[0][0])        # remove from current nodes
            buslist[fitted_list[i]].starting_nodes.remove(partner_node[0][0])       # remove from starting nodes
            nodes_checked.append(partner_node[0][0])                                # add to checked nodes
            buslist[fitted_list[i]].removed_nodes.append(partner_node[0][1])
            buslist[fitted_list[i]].current_nodes.remove(partner_node[0][1])
            buslist[fitted_list[i]].starting_nodes.remove(partner_node[0][1])
            nodes_checked.append(partner_node[0][1])
    for i in range(len(buslist)):
        buslist[i].actual_position = buslist[i].PositionCalculator(buslist[i].starting_nodes)    # Generate new dictionary with the actual positions of the nodes
    return buslist, nodes_checked

def GenerateBusDict(buslist):                                       # Generates a dictionary with the nodenames as keys and the index of the bus as value
    busdict = dict()
    for i in range(len(buslist)):
        bus = buslist[i]                                            # Referred Number of Bus
        for j in range(len(bus.starting_nodes)):
            busdict[bus.starting_nodes[j]] = i                      # Nodes as keys with number of bus i as value
    return busdict

def CalculateCost(buslist,unfitting_nodes):                     # Calculate the cost of all routes and sum them uü
    for i in range(len(buslist)):
        buslist[i].current_nodes = buslist[i].best_nodes
    overall_distance = 0
    overall_denied_nodes = 0
    operational_cost = 0
    consumption_per_100_km = Parameters.consumption_per_100_km
    cost_per_l = Parameters.cost_per_l
    overall_waiting_time = 0
    overall_in_vehicle_time = 0
    denied_nodes_list = []
    for i in range(len(buslist)):
        overall_distance += (buslist[i].OverallDistanceCalculator(buslist[i].best_nodes))[0]            # Sum of distances of all routes
        in_vehicle_time = CalculateInVehicleTime(buslist[i],buslist[i].best_schedule)
        if buslist[i].best_nodes:                                       # if route has any nodes
            operational_cost += Parameters.cost_driver                  # Add Cost of driver
        overall_in_vehicle_time += sum(in_vehicle_time)
        if buslist[i].best_nodes:
            buslist[i].CalculateSchedule()
            buslist[i].UpdateTimeWindows()  # Rearrange the order of "Route.time_earliest_departure_current" and "Route.time_latest_arrival_current" that it is in the same order as in the current sequence
            buslist[i].UpdateSchedule(buslist[i].schedule)
            denied_nodes, waiting_time, route = Testing_NewSchedule.CalculateScheduleNew(buslist[i])   # Calculate waiting time and denied nodes
            overall_waiting_time += waiting_time
            denied_nodes_list.extend(denied_nodes)
            overall_denied_nodes += len(denied_nodes)
    operational_cost += overall_distance * consumption_per_100_km / 100 * cost_per_l   # Calculate opeartional costs
    service_costs = Parameters.VoT * (overall_waiting_time * 2 + overall_in_vehicle_time)   # Calculate user costs
    print("Overall denied nodes:" + str(overall_denied_nodes))
    cost = Parameters.weighing_operational * operational_cost + Parameters.weighing_service * service_costs + Parameters.weighing_denied_requests * (overall_denied_nodes + len(unfitting_nodes))
    return cost, service_costs, operational_cost, overall_waiting_time, overall_in_vehicle_time, overall_distance, denied_nodes_list


def CalculateEmissions(distance, vehicletype):                         # Average CO2 emissions in g/km
    if vehicletype == "Bus":
        emissions = distance * Parameters.CO2_emission_Bus
    elif vehicletype == "Car":
        emissions = distance * Parameters.CO2_emissions_Car
    return emissions


def CalculateMaxOnBoardTime(duration):   # Calculate maximal on-board time if no latest arrival was chosen by the passenger
    if duration <= 4:
        OBT = 30
    elif duration > 4 and duration <= 9:
        OBT = 35
    elif duration > 9 and duration <= 14:
        OBT = 40
    elif duration > 14 and duration <= 19:
        OBT = 45
    elif duration > 19 and duration <= 24:
        OBT = 50
    elif duration > 24 and duration <= 29:
        OBT = 60
    elif duration > 29 and duration <= 34:
        OBT = 75
    else:
        OBT = 90
    return OBT

def FitEstimatedTime(nodes,time_windows_est,route_list):
    # Rearranges the attributes "estimated time-window" from input in the same order as the nodes from the result
    nodes = list(itertools.chain(*nodes))                           # Need list of nodes instead of tuples
    time_windows_est = list(itertools.chain(*time_windows_est))
    time_windows_route = []
    for i in range(len(route_list)):
        time_windows_list = []
        for j in range(len(route_list[i].best_nodes)):
            evaluated_node = route_list[i].best_nodes[j]            # retrieve a single node
            index_node = nodes.index(evaluated_node)                # get index where it was at the input
            time_windows_list.append(time_windows_est[index_node])
        time_windows_route.append(time_windows_list)                # add the fitting estimated time to the list
    return time_windows_route

def PutInRightOrder(nodes,time_windows, demand_pass, demand_pack, time_window_est):
    # Change sequence that they are the same as the departure time
    departure = [lis[0] for lis in time_windows]
    departure, nodes, time_windows, demand_pass, demand_pack, time_window_est = zip(*sorted(zip(departure, nodes, time_windows, demand_pass, demand_pack, time_window_est)))
    demand_pass = list(demand_pass)
    demand_pack = list(demand_pack)
    return nodes, time_windows, demand_pass, demand_pack, time_window_est

def CheckNodes(Route):
    # Adds removed nodes, which are not fitting in the route, to the attribute "best denied"
    nodelist = Route.best_nodes[:]
    nodelist.extend(Route.best_denied)
    for i in range(len(Route.removed_nodes)):
        if Route.removed_nodes[i] not in nodelist:
            Route.best_denied.append(Route.removed_nodes[i])
    return Route



def UpdateRoute(Route):
    # Update the Route after changing the starting nodes
    Route.actual_position = Route.PositionCalculator(Route.starting_nodes)  # Generates a dictionary, where the value is the indexnumber of the stop (key) in the starting sequence (and therefore the origin is ALWAYS before the destination)
    Route.current_position = Route.PositionCalculator(Route.current_nodes)
    Route.CalculateSchedule()
    Route.UpdateTimeWindows()  # Rearrange the order of "Route.time_earliest_departure_current" and "Route.time_latest_arrival_current" that it is in the same order as in the current sequence
    Route.UpdateSchedule(Route.schedule)
    denied_nodes, overall_waiting_time, Route = Testing_NewSchedule.CalculateScheduleNew(Route)
    Route.best_schedule = Route.schedule
    Route.MaxCapacityEvaluator()
    return Route

def ClearRoute(Route):          # Set all attributes of a route to empty or 0
    Route.starting_nodes = []
    Route.best_nodes = []
    Route.schedule = []
    Route.best_denied = []
    Route.best_cost = 0
    Route.actual_position = []
    Route.current_position = []
    Route.demand_trip = []
    Route.demand_node_starting = []
    Route.demand_node_current = []
    Route.demand_starting_route = []
    Route.demand_route = []
    Route.best_demand_route = []
    Route.demand_node_package_current = []
    Route.demand_package_route = []
    Route.time_earliest_departure_starting = []
    Route.time_latest_arrival_starting = []
    Route.time_latest_arrival_current = []
    Route.time_earliest_departure_current = []
    Route.schedule = []
    Route.best_schedule = []
    Route.origin_nodes = []
    Route.destination_nodes = []
    Route.schedule_origin = []
    Route.schedule_arrival = []
    Route.best_overall_waiting_time = 0
    return Route

def CompareRoutes(cost_list, new_cost, route_list_overall, new_route_list, best_overall_cost, scores_insertion, scores_removal, id_insertion, id_removal):
    # Updates the Scores of the ALNS
    new_route = True
    if new_cost < best_overall_cost:                    # New best overall solution
        scores_insertion[id_insertion] += 33
        scores_removal[id_removal] += 33
    elif new_cost in cost_list:
        for i in range(len(route_list_overall)):        # Check if the solution is new
            for j in range(len(new_route_list)):
                if new_route_list[j].best_nodes == route_list_overall[i][j].best_nodes:
                    new_route = False                   # There was a solution which is the same as before
                    break
        if new_route:                                   # New solution but not the best
            if new_cost < cost_list[-1]:
                scores_insertion[id_insertion] += 10
                scores_removal[id_removal] += 10
            else:                                       # Found a solution
                scores_insertion[id_insertion] += 5
                scores_removal[id_removal] += 5
    cost_list.append(new_cost)
    route_list_overall.append(new_route_list)
    return cost_list, route_list_overall, best_overall_cost, scores_insertion, scores_removal

def AdaptWeighs(scores_insertion, scores_removal, weighs_insertion, weighs_removal, number_insertion, number_removal):
    # Calculate new weights of the ALNS after a certain number of iterations (in this case 100)
    reaction_factor = 0.1
    weighs_insertion_list = weighs_insertion[:]
    for i in range(len(weighs_insertion)):
        if number_insertion[i] != 0:
            weighs_insertion_list[i] = weighs_insertion[i]*(1-reaction_factor) + reaction_factor*(scores_insertion[i]/number_insertion[i])
    for i in range(len(weighs_insertion_list)):
        weighs_insertion[i] = weighs_insertion_list[i]/sum(weighs_insertion_list)
    weighs_removal_list = weighs_removal[:]
    for i in range(len(weighs_removal)):
        if number_removal[i] != 0:
            weighs_removal_list[i] = weighs_removal[i]*(1-reaction_factor) + reaction_factor*(scores_removal[i]/number_removal[i])
    for i in range(len(weighs_removal_list)):
        weighs_removal[i] = weighs_removal_list[i]/sum(weighs_removal_list)
    scores_removal = [0,0,0]
    scores_insertion = [0,0,0]
    return weighs_removal, weighs_insertion, scores_removal, scores_insertion

def CalculateInVehicleTime(Route, schedule):
    # Calculate the new in-vehicle time
    in_vehicle_time = []
    actual_position_dict = Route.actual_position
    current_position_dict = Route.PositionCalculator(Route.current_nodes)
    for i in range(len(Route.current_nodes)):
        index_node = actual_position_dict.get(Route.current_nodes[i])       # get the actual position index of the node --> Origin or Destination
        if index_node % 2 == 0:                                        # only check origins
            if int(Route.current_nodes[i].split('.')[1]) > 1000:        # package does not have in-vehicle-time
                in_vehicle_time.append(0)
            else:
                name_trip_partner = list(actual_position_dict.keys())[list(actual_position_dict.values()).index(index_node + 1)]
                index_destination = current_position_dict.get(name_trip_partner)        # current index of destination
                if index_destination:  # if destination is not inserted yet, there is not in-vehicle time to be calculated
                    in_vehicle_time.append(schedule[index_destination]-schedule[i])         # Cacluate the time-difference between origin/destination in the schedule
    return in_vehicle_time

def CalculateCostInsertion(distance,Route, denied_nodes, waiting_time, schedule):
    # Calculates the cost for inserting a node
    in_vehicle_time = sum(CalculateInVehicleTime(Route, schedule))
    consumption_per_100_km = 11
    cost_per_l = Parameters.cost_per_l
    cost_driver = Parameters.cost_driver
    operational_cost = distance * consumption_per_100_km/100 * cost_per_l + cost_driver
    service_cost = Parameters.VoT * (in_vehicle_time + 2 * waiting_time)
    cost = Parameters.weighing_operational * operational_cost + Parameters.weighing_service * service_cost + Parameters.weighing_denied_requests * len(denied_nodes)
    return cost
