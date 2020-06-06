import csv
import matplotlib.pylab as plt
import numpy as np
import math
import HelpingFunctions
import Route
import Testing_DataFLEXIBUS
import Parameters
import DemandSets
import time
import copy
import Removal_Operations
import Insertion_Operations

if __name__ == "__main__":


    with open('Stops_Krumbach.csv', mode='r') as infile:
    # Read all the possible stops in Krumbach
        reader = csv.reader(infile, delimiter=';')
        for rows in reader:
            mydict = {rows[0]: (rows[2], rows[3]) for rows in reader}

    stop_csv = 'Stops_Krumbach.csv'
    route_csv = Parameters.route
    runs = Parameters.number_runs

    best_route_runs = []
    operational_cost_runs = []
    service_cost_runs = []
    best_cost_runs = []
    cost_list_runs = []
    best_cost_list_runs = []
    best_waiting_time_runs = []
    best_in_vehicle_time_runs = []
    best_distance_runs = []

    package_insertion = Parameters.package_insertion
    scenario_number = Parameters.scenario_number
    scenario_load = Parameters.scenario_load

    for run in range(runs):
        nodes, time_window, time_windows_est, route_fixed, route_fare, bla = Testing_DataFLEXIBUS.ImportFLEXIBUSData(stop_csv,route_csv)

        if package_insertion:
            nodes, time_window, time_windows_est = DemandSets.Integration(nodes,time_window,time_windows_est)
        if Parameters.separation:
            nodes, time_window, time_windows_est = DemandSets.ParameterSeparation()

        demand_passenger = []
        demand_package = []
        for i in range(len(nodes)):
            if int(nodes[i][0]) > 9000 and int(nodes[i][1]) > 9000:     # If Stop is no shop --> add passenger
                demand_passenger.append(1)
                demand_package.append(0)
            else:                                                       # If stop is shop/pickup station --> add package
                demand_passenger.append(0)
                demand_package.append(1)

        nodes, time_window, demand_passenger, demand_package, time_windows_est = HelpingFunctions.PutInRightOrder(nodes,time_window, demand_passenger, demand_package, time_windows_est)
        main_route = Route.route(nodes, demand_passenger, mydict, time_window, demand_package)

        index_passengers = len(nodes)-1
        degree_of_deconstruction = Parameters.degree_of_deconstruction
        route_list = []
        nodes_fixed = HelpingFunctions.GenerateTuple(main_route.starting_nodes)

        if Parameters.predefined_no_busses == 3:        # Distribute if number of busses is 3
            nodes_1 = nodes_fixed[0::3]
            nodes_2 = nodes_fixed[1::3]
            nodes_3 = nodes_fixed[2::3]
            time_window_1 = time_window[0::3]
            time_window_2 = time_window[1::3]
            time_window_3 = time_window[2::3]
            demand_pack_1 = demand_package[0::3]
            demand_pack_2 = demand_package[1::3]
            demand_pack_3 = demand_package[2::3]
            demand_pass_1 = demand_passenger[0::3]
            demand_pass_2 = demand_passenger[1::3]
            demand_pass_3 = demand_passenger[2::3]
            route_1 = Route.route(nodes_1,demand_pass_1,mydict,time_window_1, demand_pack_1)
            route_2 = Route.route(nodes_2,demand_pass_2,mydict,time_window_2, demand_pack_2)
            route_3 = Route.route(nodes_3,demand_pass_3,mydict,time_window_3, demand_pack_3)
            route_list = [route_1, route_2, route_3]

        if Parameters.predefined_no_busses == 2:        # Distribute if number of busses is 2
            nodes_1 = nodes_fixed[0::2]
            nodes_2 = nodes_fixed[1::2]
            time_window_1 = time_window[0::2]
            time_window_2 = time_window[1::2]
            demand_pack_1 = demand_package[0::2]
            demand_pack_2 = demand_package[1::2]
            demand_pass_1 = demand_passenger[0::2]
            demand_pass_2 = demand_passenger[1::2]
            route_1 = Route.route(nodes_1,demand_pass_1,mydict,time_window_1, demand_pack_1)
            route_2 = Route.route(nodes_2,demand_pass_2,mydict,time_window_2, demand_pack_2)
            route_list = [route_1, route_2]
        unfitting_nodes = []

        best_overall_cost = 50000000
        result_list = []
        scores_insertion = [0,0,0]
        scores_removal = [0,0,0]
        if len(route_list) > 2: # predefine weighs
            weighs_insertion = [0.33,0.33,0.33]
            number_insertion = [0, 0, 0]
        else:
            weighs_insertion = [0.5,0.5]    # no regret-3-heuristic --> only 2 heuristics tested
            number_insertion = [0, 0]
        weighs_removal = [0.33,0.33,0.33]
        number_removal = [0,0,0]
        route_list_overall = []
        cost_list = []
        operational_cost_list =[]
        service_cost_list = []
        best_cost_list = []
        number_of_iteration = Parameters.number_iterations


    # ------ Optimize node-distribution among different busses -------
        for i in range(number_of_iteration):
            start = time.process_time()
            print("Optimiziation step" + str(i))
            node_list = []
            for k in range(len(route_list)):                        #Need to do it this way, because unfitting nodes dont need to be removed because they are not in a route currently
                node_list.extend(route_list[k].current_nodes)
            removed_nodelist, indexes, id_removal, number_of_runs = Removal_Operations.RemoveNodes(main_route,route_list, degree_of_deconstruction, node_list, weighs_removal, number_removal)
            test_dict = HelpingFunctions.GenerateBusDict(route_list)                                                # Get Dictionary, which shows, in which bus each node is {'1.1': 0, '2.0':1, '5.0': 1}
            route_list, removed_nodelist = HelpingFunctions.RemoveNodes(route_list, test_dict, removed_nodelist)
            removed_nodelist = []
            for p in range(len(route_list)):
                removed_nodelist.extend(route_list[p].removed_nodes)        # get all removed nodes
            route_list_output = []
            route_list, unfitting_nodes, id_insertion, number_insertion = Insertion_Operations.InsertNodes(route_list, demand_passenger ,time_window, mydict, unfitting_nodes,removed_nodelist, weighs_insertion, number_insertion, demand_package)
            number_inserted_nodes = 0
            print("Unfitting Nodes after insertion:" + str(unfitting_nodes))
            for j in range(len(route_list)):
                print("Route List Later" + str(route_list[j].best_nodes))
                number_inserted_nodes += len(route_list[j].best_nodes)
            print("Number inserted nodes:" + str(number_inserted_nodes))
            overall_cost, service_costs, operational_cost, overall_waiting_time, in_vehicle_time, distance, denied_nodes = HelpingFunctions.CalculateCost(route_list, unfitting_nodes)
            # Store costs in a list for plotting
            service_cost_list.append(service_costs)
            operational_cost_list.append(operational_cost)
            cost_list, route_list_overall, best_overall_cost, scores_insertion, scores_removal = HelpingFunctions.CompareRoutes(cost_list, overall_cost, route_list_overall, route_list, best_overall_cost, scores_insertion,scores_removal, id_insertion, id_removal)  # Checks, whether the solution was already found

            if i % 100 == 0 and i > 1:      # Update weighs after 100 iterations
                weighs_removal, weighs_insertion, scores_removal, scores_insertion = HelpingFunctions.AdaptWeighs(scores_insertion, scores_removal, weighs_insertion, weighs_removal, number_insertion, number_removal)
            print(overall_cost)
            if overall_cost < best_overall_cost:        # Check if new optimum
                # Update the best attributes
                index_best_run = copy.copy(i)
                best_overall_cost = copy.copy(overall_cost)
                best_operational_cost = copy.copy(operational_cost)
                best_service_cost = copy.copy(service_costs)
                print("Found new optimum!")
                best_route_list = copy.deepcopy(route_list)
                best_unfitting_nodes = unfitting_nodes[:]
                best_denied_nodes = copy.copy(denied_nodes)
                best_waiting_time = copy.copy(overall_waiting_time)
                best_in_vehicle_time = copy.copy(in_vehicle_time)
                best_distance = copy.copy(distance)
            best_cost_list.append(best_overall_cost)

        # Export best route as csv file
        filename = 'test_outcome' + str(run) + '.csv'
        time_windows_est_adjusted = HelpingFunctions.FitEstimatedTime(nodes_fixed, time_windows_est, best_route_list)
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            for q in range(len(best_route_list)):
                writer.writerow(best_route_list[q].best_nodes)
                writer.writerow(best_route_list[q].best_schedule)
                writer.writerow(time_windows_est_adjusted[q])
                writer.writerow(best_route_list[q].best_denied)
            writer.writerow(best_unfitting_nodes)
            writer.writerow(best_denied_nodes)


        # store best results for each run
        best_route_runs.append(best_route_list)
        operational_cost_runs.append(best_operational_cost)
        service_cost_runs.append(best_service_cost)
        best_cost_runs.append(best_overall_cost)
        best_cost_list_runs.append(best_cost_list)
        cost_list_runs.append(cost_list)
        best_in_vehicle_time_runs.append(best_in_vehicle_time)
        best_waiting_time_runs.append(best_waiting_time)
        best_distance_runs.append(best_distance)
        print("Zeit 1 Iteration:" + str(time.process_time() - start))

    # -------------------- RESULTS FOR KPIS ----------------------------

    emissions = []
    for i in range(len(best_distance_runs)):
        emissions.append(HelpingFunctions.CalculateEmissions(best_distance_runs[i],"Bus"))
    print("IVT:" + str(best_in_vehicle_time_runs))
    print("WT:" + str(best_waiting_time_runs))
    print("OC" + str(operational_cost_runs))
    print("SC" + str(service_cost_runs))
    print("DIST:" + str(best_distance_runs))
    print("CO2:" + str(emissions))
    print("BC:" + str(best_cost_runs))


    # ----------------------- PLOTTING OF SOME RESULTS --------------------------

    plt.figure(1)
    #plt.subplot(211)
    for i in range(runs):
        plt.plot(range(number_of_iteration),best_cost_list_runs[i], color='b')
    plt.title("Best costs of various runs")
    plt.xlabel("Number of iterations")
    plt.ylabel("Costs")
    #plt.legend()
    plt.figure(2)
    #plt.subplot(212)
    for i in range(runs):
        plt.plot(range(number_of_iteration), cost_list_runs[i], color='g')
    plt.title("Current costs of various runs")
    plt.xlabel("Number of iterations")
    plt.ylabel("Costs")
    #plt.legend()

    plt.figure(3)
    #plt.subplot(211)
    plt.plot(range(1,runs+1), operational_cost_runs, color='r', linestyle="None", marker='o')
    plt.title("Best Operational costs of various runs")
    plt.xlabel("Number of runs")
    plt.ylabel("Costs")
    #plt.subplot(212)
    plt.figure(4)
    plt.plot(range(1,runs+1), service_cost_runs, color='c', linestyle="None", marker='o')
    plt.title("Best Service Costs of various runs")
    plt.xlabel("Number of runs")
    plt.ylabel("Costs")

    plt.show()

    plt.figure(1)
    plt.subplot(211)
    plt.plot(range(number_of_iteration), operational_cost_list)
    plt.plot(range(number_of_iteration), service_cost_list)
    plt.legend(['Operational costs','Service costs'])
    plt.xlabel("Number of iterations")
    plt.ylabel("Costs")
    plt.subplot(212)
    plt.plot(range(number_of_iteration), best_cost_list)
    plt.plot(range(number_of_iteration), cost_list)
    plt.legend(['Best Costs','Current Costs'])
    plt.xlabel("Number of iterations")
    plt.ylabel("Costs")
    plt.show()
