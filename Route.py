import Testing_Time
from datetime import timedelta
import HelpingFunctions
import GetMatrizes
import itertools


class route(object):

    def __init__(self,nodes,demand,dict,time_windows, demand_package):                                                      # nodes is list of testnode (e.g. [('1','2'),('3','4')] ), demand is number of people of the trip and dict ist the dictionary with nodename and coords from the CSV
        self.dictionary                         = dict
        self.current_nodes                      = self.CreateNodelist(nodes,dict)
        self.best_nodes                         = self.CreateNodelist(nodes,dict)
        self.starting_nodes                     = self.CreateNodelist(nodes,dict)
        self.removed_nodes                      = []
        self.current_overall_dist, self.distance_list       = self.OverallDistanceCalculator(self.current_nodes)   # cost_list is important for WorstRemoval
        self.best_cost                          = 50000000
        self.actual_position                    = self.PositionCalculator(self.starting_nodes)                  # Generates a dictionary, where the value is the indexnumber of the stop (key) in the starting sequence (and therefore the origin is ALWAYS before the destination)
        self.current_position                   = self.PositionCalculator(self.current_nodes)
        self.demand_trip                        = demand                                                        # demand for each trip, e.g. [('1','2')] has demand [2]
        self.demand_node_starting               = self.CreateDemandNode(self.demand_trip)                       # sequence of demands for each separate node [1,-1,2,-2,3,-3] in the starting order
        self.demand_node_current                = self.CreateDemandNode(self.demand_trip)                       # sequence of demands for each separate node [1, 3,-1,-3] for current route. NOT SUMMED UP!
        self.demand_starting_route              = self.DemandSummation(self.demand_node_starting)               # sequence for the starting route of demands. Summed up. [1,0,2,0,3,0]
        self.demand_route                       = []
        self.best_demand_route                  = []
        self.demand_package_trip                = demand_package
        self.demand_node_package_starting       = self.CreateDemandNode(self.demand_package_trip)               # similar to demand_node_starting
        self.demand_node_package_current        = self.CreateDemandNode(self.demand_package_trip)               # similar to demand_node_current
        self.demand_package_route               = self.DemandSummation(self.demand_node_package_starting)       # similar to demand_route
        self.time_earliest_departure_starting   = [lis[0] for lis in time_windows]                              # retrieve earliest departure
        self.time_latest_arrival_starting       = self.AdjustArrivalTime([lis[1] for lis in time_windows],self.time_earliest_departure_starting,self.starting_nodes)        # Calculate latest arrival
        self.time_latest_arrival_current        = self.time_latest_arrival_starting[:]
        self.time_earliest_departure_current    = self.time_earliest_departure_starting[:]
        self.time_current                       = 300
        self.time_previous_stop                 = 0
        self.schedule                           = self.CalculateSchedule()
        self.best_schedule                      = []
        self.origin_nodes                       = self.GetCurrentOriginNodes()
        self.destination_nodes                  = self.GetCurrentDestinationNodes()
        self.schedule_origin                    = Testing_Time.CalculateScheduleAtNode(self.origin_nodes,self.PositionCalculator(self.current_nodes),self.schedule)             # Calculate the schedule for all origin nodes in the current sequence
        self.schedule_arrival                   = Testing_Time.CalculateScheduleAtNode(self.destination_nodes,self.PositionCalculator(self.current_nodes),self.schedule)        # Calculate the schedule for all destination nodes in the current sequence
        self.best_denied                        = []                                                            # List of all denied nodes for the best solution
        self.best_overall_waiting_time          = 0



#----------FUNCTIONS FOR CREATING AND CHANGING NODES-------------------------------------------------------------------------
    def CreateNodelist(self,nodes, dict):
    # Create a nodelist with fitting IDs for nodes
        for i in range(len(nodes)):
            nodelist = []
            if nodes[i][0].__contains__('.'):                           # Check if nodes already have IDs
                nodelist.extend(list(itertools.chain(*nodes)))          # Nodes have IDs --> return them
                break
            else:
                for i in range(0, len(nodes)):
                    if int(nodes[i][0]) <= 9000 or int(nodes[i][1]) <= 9000:            # Check if request is for a package
                        trip, tripStart,tripEnd = self.DeliveryGenerator(dict, nodes[i], i + 10000)           # Add 10000 for ID
                        nodes_storage = list(trip.keys())
                        nodelist.extend(nodes_storage)              # Add nodes to list
                    else:
                        trip, tripStart,tripEnd = self.DeliveryGenerator(dict, nodes[i], i)
                        nodes_storage = list(trip.keys())
                        nodelist.extend(nodes_storage)
        return nodelist


    def GetCurrentDestinationNodes(self):
        # Get the current destination nodes in the right order
        destination_nodes_starting = self.starting_nodes[1::2]                                  # Get all destination nodes
        current_position = self.PositionCalculator(self.current_nodes)
        destination_nodes_current = ['xx'] * len(self.current_nodes)                            # Generate "empty" list with "xx" as placeholders
        for i in range(len(destination_nodes_starting)):
            node_position = current_position.get(destination_nodes_starting[i])
            if node_position is not None:
                destination_nodes_current[node_position] = destination_nodes_starting[i]            # Fill only the destination nodes into the index resembling their current position
        k = 0
        length = len(destination_nodes_current)
        while k < length:                                                                       # Delete all placeholder "xx"
            if destination_nodes_current[k] == 'xx':
                destination_nodes_current.remove('xx')
                length -= 1
            else:
                k +=1
        return destination_nodes_current

    def GetCurrentOriginNodes(self):
        # Get the current origin nodes in the right order
        origin_nodes_starting = self.starting_nodes[0::2]                                       # Get all origin nodes
        current_position = self.PositionCalculator(self.current_nodes)
        origin_nodes_current = ['xx'] * len(self.current_nodes)                                 # Generate "empty" list with "xx" as placeholders
        for i in range(len(origin_nodes_starting)):
            node_position = current_position.get(origin_nodes_starting[i])
            if node_position is not None:
                origin_nodes_current[node_position] = origin_nodes_starting[i]                      # Fill only the origin nodes into the index resembling their current position
        j = 0
        length = len(origin_nodes_current)
        while j < length:                                                                       # Delete all placeholder "xx"
            if origin_nodes_current[j] == 'xx':
                origin_nodes_current.remove('xx')
                length -= 1
            else:
                j +=1
        return origin_nodes_current

    def DeliveryGenerator(self,dict, input, tripID):
        # Add the ID to the request
        start_index = input[0]
        end_index = input[1]                                                        # index of the specific node for this trip in the dictionary
        if start_index.__contains__('.') or input.__contains__('.'):
            start_name = start_index
            end_name = end_index
            start_index = start_index.split('.', 1)[0]
            end_index = end_index.split('.')[0]
        else:
            start_name = str(input[0]) + '.' + str(tripID)
            end_name = str(input[1]) + '.' + str(tripID)                                # Add the index of the trip to the nodename to have a unique key
        tripStart = list(dict[start_index])
        tripEnd = list(dict[end_index])
        trip = {start_name: dict[start_index],end_name: dict[end_index]}            # Dictionary with node name and coordinates for this trip
        return trip, tripStart, tripEnd

    def OverallDistanceCalculator(self,nodelist):
        # Calculate the overall distance of the nodes
        distance_list = []
        c = 0
        for i in range(1, len(nodelist)):
            distance_list.append(GetMatrizes.GetDistance(nodelist[i-1],nodelist[i]))      # Calculate the cost between each stop --> important for WorstRemoval
            c += distance_list[i - 1]
        self.distance_list = distance_list
        return c, distance_list


    def SetRemovedNodes(self,node):
        self.removed_nodes = node

    def GetRemovedNodes(self):
        return self.removed_nodes

    def GetCurrentRoute(self):
        return self.current_nodes

    def SetBestRoute(self,coords,nodes):
        self.best_coords = coords
        self.best_nodes = nodes

    def GetBestRoute(self):
        return self.best_coords, self.best_nodes

    def SetStartingNodes(self,nodes):
        self.starting_nodes = nodes


    def SetRemovedRoute(self,coords,nodes):
        self.removed_coords = coords
        self.removed_nodes = nodes

    def GetRemovedRoute(self):
        return self.removed_coords, self.removed_nodes

    def UpdateCurrentRoute(self, nodes):
        self.current_nodes = nodes

    def SetBestCost(self,cost):
        self.best_cost = cost

    def GetBestCost(self):
        return self.best_cost

    def SetCurrentOverallDist(self,dist):
        self.current_overall_dist = dist

    def GetCurrentCost(self):
        return self.current_overall_dist

    def SetCurrentCostlist(self,dist_list):
        self.distance_list = dist_list

    def GetCurrentCostlist(self):
        return self.distance_list


    def PositionCalculator(self,nodes):
        return dict(zip(nodes, range(0, len(nodes))))

# -------------FUNCTIONS FOR DEMAND AND CAPACITY CONSTRAINT--------------------------------------------------------



    def CreateDemandNode(self,demand):
        # Takes the demand of a trip and generates list with demand for each node [1,-1,2,-2,3,-3]
        demand_insert = demand[:]
        for i in range(0, len(demand_insert) * 2, 2):
            demand_insert.insert(i + 1, -demand_insert[i])
        return demand_insert

    def DemandSummation(self,demand):
        #Takes as input a list for the demand of every node, sums them up and generates a list where the demand after visiting each node is shown
        demandlist = []
        for i in range(len(demand)):
            if i == 0:
                demandlist.append(demand[i])
            else:
                demandlist.append(demand[i] + demandlist[i - 1])
        return demandlist

    def CreateCurrentDemand(self):
        # Creates a list of the demand of each node in the current sequence, e.g. [1,2,-2,-1]
        current_demand = []                                                                 # Current demand calculated new every time --> set empty
        for i in range(len(self.current_nodes)):                                            # Adds the demand of the nodes in the current route one after another
            name_of_node = self.current_nodes[i]                                            # Looks for the name of the node to insert next, e.g. '2.0'
            index_of_node = self.actual_position.get(name_of_node)                          # Looks, where the node was standing in the original route, e.g. 1
            demand_of_node = self.demand_node_starting[index_of_node]                       # Retrieves the demand value of the node, e.g. -2
            current_demand.append(demand_of_node)                                           # Appends the demand for each node to the current_demand list
        return current_demand


    def MaxCapacityEvaluator(self):
        # Calculate the maximum demand of passengers during the whole route
        demand_node_current = self.CreateCurrentDemand()
        demand_current_route = self.DemandSummation(demand_node_current)        # Sum all single requests
        self.demand_route = demand_current_route
        maximum_demand = max(demand_current_route)
        return maximum_demand

#-----------FUNCTIONS FOR TIME-WINDOW CONSTRAINT--------------------------------

    def AdjustArrivalTime(self,times_arrival,times_dep,nodes):
        # Adjust the arrival time if no latest arrival time was selected
        output = []
        for i in range(len(times_arrival)):
            if times_arrival[i] == 'empty':     # no arrival time selected
                duration = GetMatrizes.GetDuration(nodes[2*i],nodes[2*i+1])   # calculate the regular duration
                maximum_onb = HelpingFunctions.CalculateMaxOnBoardTime(duration)
                output.append(times_dep[i]+maximum_onb)    # Caclualte adjusted arrival time
            else:
                output.append(times_arrival[i])
        return output


    def GetDurationList(self,nodelist):
        # Get a list of durations between the following nodes [2,5,10,2,7]
        duration_list = []
        for i in range(1, len(nodelist)):
            duration_list.append(GetMatrizes.GetDuration(nodelist[i-1],nodelist[i]))
        return duration_list


    def CalculateSchedule(self):
    # Calculates the Schedule of the current route with the first array being the current time [0,15,25,30,35,40]
        schedule = [0]
        duration = self.GetDurationList(self.current_nodes)                                             # DURATION NOT EQUAL DISTANCE!!!
        if duration != []:
            schedule[0] = duration[0]                                                 # Take the first entry of the costlist for the first stop
        for i in range(len(duration)):
            end_index = int(self.current_nodes[i].split('.')[1])
        for i in range(1,len(duration)):
            schedule.append(schedule[i-1]+duration[i])                            # sum up time over the route
        schedule = [x + self.time_current for x in schedule]                      # add the time of the previous stop to all nodes that the time is right
        schedule.insert(0,self.time_current)                                      # insert the current time at the place --> "node zero"
        self.schedule = schedule
        return schedule

    def UpdateSchedule(self,new_schedule):
        # Updates the schedule after changing the schedule, for example after a bus has to wait at the departure for the passenger. Needed to sepraete origin/destination
        self.schedule = new_schedule[:]
        self.schedule_origin                = Testing_Time.CalculateScheduleAtNode(self.GetCurrentOriginNodes(),self.PositionCalculator(self.current_nodes),self.schedule)
        self.schedule_arrival               = Testing_Time.CalculateScheduleAtNode(self.GetCurrentDestinationNodes(),self.PositionCalculator(self.current_nodes),self.schedule)
        self.origin_nodes                   = self.GetCurrentOriginNodes()
        self.destination_nodes              = self.GetCurrentDestinationNodes()

    def UpdateTimeWindows(self):
    # Rearranges the sequence of the time-window list that it complies with the sequence of the current route.
        time_earliest_departure_starting = self.time_earliest_departure_starting[:]    # Get earliest departure time in the starting sequence
        time_latest_arrival_starting = self.time_latest_arrival_starting[:]
        current_position = self.PositionCalculator(self.current_nodes)
        arrival_nodes = self.starting_nodes[1::2]               # Get all destinations
        departure_nodes = self.starting_nodes[0::2]             # Get all origins
        time_dep_current = ['xx'] * len(self.current_nodes)
        time_arr_current = ['xx'] * len(self.current_nodes)
        for i in range(len(time_earliest_departure_starting)):      # Gets over all nodes
            actual_value_time_dep = time_earliest_departure_starting[i]     # Take the earliest departure time of the i-th entry
            actual_value_time_arr = time_latest_arrival_starting[i]         # Take the latest arrival time of the i-th entry (fitting destination=
            current_position_time_dep = current_position.get(departure_nodes[i])        # Get the current position of departure node
            if current_position_time_dep is not None:                                   # if it has an index
                time_dep_current[current_position_time_dep] = actual_value_time_dep     # fit in right position
            current_position_time_arr = current_position.get(arrival_nodes[i])          # Get current position of arrival node
            if current_position_time_arr is not None:                                   # if it has an index
                time_arr_current[current_position_time_arr] = actual_value_time_arr     # fit in right position
        k = 0
        length = len(time_dep_current)
        while k < length:
            if time_dep_current[k] == 'xx':         # Remove placeholders
                time_dep_current.remove('xx')
                length -= 1
            else:
                k +=1
        l = 0
        length2 = len(time_arr_current)
        while l < length2:
            if time_arr_current[l] == 'xx':         # Remove placeholders
                time_arr_current.remove('xx')
                length2 -= 1
            else:
                l += 1
        self.time_earliest_departure_current = time_dep_current[:]
        self.time_latest_arrival_current = time_arr_current[:]


    def GetScheduleClock(self):
        # Transforms the schedule with only minutes to a regular time-format [13:30, 13:45, 14:00]
        schedule = []
        self.CalculateSchedule()
        for i in range(len(self.schedule)):
            schedule.append(timedelta(minutes=self.schedule[i]))
        return schedule


# --------- FUNCTIONS FOR PACKAGE INSERTION

    def MaxCapacityEvaluatorPackage(self):
        # Calculates the current maximal number of packages during the route of the bus
        demand_current_route = self.DemandSummation(self.demand_node_package_current) # Sums up all the single package demands
        self.demand_package_route = demand_current_route
        maximum_demand_package = max(demand_current_route)      # find maximum
        return maximum_demand_package



