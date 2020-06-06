import Testing_Time
import Parameters


def CalculateScheduleNew(route):
    # Calculates the schedule of the route
    current_schedule = route.schedule[:]
    earliest_dep_starting = route.time_earliest_departure_starting
    latest_arrival_starting = route.time_latest_arrival_starting
    overall_waiting_time = 0
    denied_nodes = []
    for i in range(len(route.current_nodes)):
        index_node_starting = route.actual_position.get(route.current_nodes[i])         # Index --> Origin or Destination
        end_index = int(route.current_nodes[i].split('.')[1])
        if index_node_starting % 2 == 0:             # It is an origin --> Departure
            if end_index < 10000:           # Trip is for a passenger
                time_window = Testing_Time.CalculateTimewindowDeparture(earliest_dep_starting[int(index_node_starting/2)])  # creates list with tuples of time-windows
                boarding_time = Parameters.Boarding_time_passenger
            else:                           # Trip is for a package
                time_window = Testing_Time.CalculateTimewindowDeparturePackage(earliest_dep_starting[int(index_node_starting/2)])
                boarding_time = Parameters.Boarding_time_package
            bus_waiting_time = 0
            if current_schedule[i] < time_window[0]:            # Calculates if the bus has to wait for the request
                bus_waiting_time = time_window[0] - current_schedule[i]
            current_schedule[i] = current_schedule[i] + bus_waiting_time        # All later requests are affected by the waiting time
            if i < len(current_schedule) - 2:
                if int(route.current_nodes[i].split('.')[0]) == int(route.current_nodes[i+1].split('.')[0]):    # Same node --> only add boarding time once
                    boarding_time = 0
            for j in range(i+1, len(current_schedule)):
                current_schedule[j] = current_schedule[j] + bus_waiting_time + boarding_time        # calculate the schedule for this node (taking care of waiting time and boarding time)
            if current_schedule[i] == time_window[0]:   # schedule and departure time are the same
                continue
            elif time_window[0] <= current_schedule[i] <= time_window[1] :  # later than the earliest departure time but before the latest departure time
                if end_index < 1000:        # if passenger --> Calculate KPI waiting time
                    waiting_time = Testing_Time.CalculateWaitingTime(time_window[0], current_schedule[i])
                    overall_waiting_time += waiting_time
            else:       # later than latest departure --> denied
                denied_nodes.append(route.current_nodes[i])
        elif index_node_starting % 2 != 0:      # Arrival at destination
            if end_index < 10000:               # passenger
                time_window = Testing_Time.CalculateTimewindowArrival(latest_arrival_starting[int(index_node_starting/2)])
            else:                               # package --> has delivery time
                time_window = Testing_Time.CalculateTimewindowArrivalPackage(latest_arrival_starting[int(index_node_starting/2)])
                delivery_time = Parameters.Delivery_time_package
                bus_waiting_time = 0
                if i < len(current_schedule)-1:
                    if int(route.current_nodes[i].split('.')[0]) == int(route.current_nodes[i+1].split('.')[0]):  # Same node --> only add delivery time once
                        delivery_time = 0
                if current_schedule[i] < time_window[0] and Parameters.scenario_number != 2:            # Packages can be denied if delivered too early for scenario 1 and 3 --> wait
                    bus_waiting_time = time_window[0] - current_schedule[i]                 # Calculate waiting time of bus
                    current_schedule[i] = current_schedule[i] + bus_waiting_time
                for j in range(i + 1, len(current_schedule)):                               # Calculate current schedule for this node
                    current_schedule[j] = current_schedule[j] + bus_waiting_time + delivery_time
                if current_schedule[i] > time_window[0]:
                    current_schedule
            if time_window[1] < current_schedule[i]:                        # Bus cannot reach node within time window --> request is denied
                denied_nodes.append(route.current_nodes[i])
    route.UpdateTimeWindows()
    route.UpdateSchedule(current_schedule)
    return denied_nodes, overall_waiting_time, route