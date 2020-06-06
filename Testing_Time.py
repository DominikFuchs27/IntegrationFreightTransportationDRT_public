import Parameters

def CalculateTimewindowDeparture(earliest_time):
    time_gap = 20
    latest_time = earliest_time + time_gap
    time_window = (earliest_time, latest_time)
    return time_window

def CalculateTimewindowDeparturePackage(earliest_time):
    if Parameters.scenario_number == 1 or Parameters.scenario_number == 2:
        time_gap = 30
    else:
        time_gap = 60
    latest_time = earliest_time+time_gap
    time_window = (earliest_time, latest_time)
    return time_window

def CalculateTimewindowArrival(latest_time):
    time_gap = 40
    earliest_time = latest_time-time_gap
    time_window = (earliest_time, latest_time)
    return time_window

def CalculateTimewindowArrivalPackage(latest_time):
    if Parameters.scenario_number == 1 or Parameters.scenario_number == 3:
        time_gap = 30
    else:
        time_gap = 60
    earliest_time = latest_time-time_gap
    time_window = (earliest_time, latest_time)
    return time_window

def CalculateWaitingTime(pickup_time,dropoff_time):
    return dropoff_time-pickup_time

def CalculateAdditionalWaitingTime (pickup_time, earliest_time):
    return pickup_time-earliest_time

def CalculateInvehicleTime(pickup_time,dropoff_time):
    return dropoff_time-pickup_time


def CalculateScheduleAtNode(nodelist,route_current_position_dict,schedule):
    current_position_dict = dict(route_current_position_dict)
    schedule_at_nodes = []
    for i in range(0,len(nodelist)):
        index_destination_node_current = current_position_dict.get(nodelist[i])
        schedule_node_current = schedule[index_destination_node_current]
        schedule_at_nodes.append(schedule_node_current)
    return schedule_at_nodes

def DepartureChecker(dep_nodes,schedule_dep,earliest_dep,route):                                # DEPARTURE NODES IN ORDER OF CURRENT ROUTE!!!
    current_nodes = route.GetCurrentRoute()
    current_position_dict = route.PositionCalculator(current_nodes)                             # Creates dictionary with name of node as key and position as value
    current_cost = route.schedule[:]                                                            # need to copy schedule attribute from route class to prohibit overwritting
    timewindows = []
    for i in range(len(schedule_dep)):
        end_index = int(dep_nodes[i].split('.')[1])
        if end_index < 10000:                                                                       # Trip is for a passenger
            timewindows.append(CalculateTimewindowDeparture(earliest_dep[i]))                       # creates list with tuples of time-windows
            boarding_time = Parameters.Boarding_time_passenger
        else:                                                                                       # Trip is for a package
            timewindows.append(CalculateTimewindowDeparturePackage(earliest_dep[i]))
            boarding_time = Parameters.Boarding_time_package
        timewindow = timewindows[i]                                                             # current time window is i
        index_origin_node_current = current_position_dict.get(route.origin_nodes[i])                # retrieves the index, where the investigated route is in the current route
        if schedule_dep[i] < timewindow[0]:                                                     # SITUATION A: The bus arrives earlier than the earliest departure of passenger --> has to wait --> all visits are postponed
            bus_waiting_time = timewindow[0]-schedule_dep[i]                                    # Waiting time of the bus until the passenger is ready to leave
            for j in range(index_origin_node_current,len(current_cost)):
                if j < len(current_nodes)-1 and current_nodes[j].split('.')[0] == current_nodes[j+1].split('.')[0]:      # Checks if there are consecutive nodes --> no additional boarding time
                    current_cost[j] = current_cost[j]+bus_waiting_time
                else:
                    current_cost[j] = current_cost[j]+bus_waiting_time+boarding_time        # All nodes in the route, which appear after the node with waiting time, are delayed with the amount of time the bus has to wait
            schedule_dep = CalculateScheduleAtNode(route.origin_nodes,route.PositionCalculator(route.current_nodes), current_cost)
    overall_waiting_time = 0
    denied_nodes = []
    for i in range(len(schedule_dep)):
        index_destination_node_current = current_position_dict.get(dep_nodes[i])
        timewindow = timewindows[i]
        if current_cost[index_destination_node_current] == timewindow[0]:                       # SITUATION B: Bus is on time (either because planned or after waiting at stop)
            continue
        elif timewindow[0] <= current_cost[index_destination_node_current] <= timewindow[1]:     # SITUATION C: Bus is delayed but within the time window
            waiting_time = CalculateWaitingTime(timewindow[0],current_cost[index_destination_node_current])
            overall_waiting_time += waiting_time                                                # sum of all delays
        else:                                                                                   # SITUATION D: Bus cannot reach node within time window --> request is denied
            denied_nodes.append(dep_nodes[i])                                                   # list with the name of all denied nodes
    return denied_nodes, overall_waiting_time, current_cost
