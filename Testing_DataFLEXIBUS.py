import csv
import pandas
import datetime as dt
import numpy as np
import math
import GetMatrizes
import HelpingFunctions
import itertools
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def ImportFLEXIBUSData(Stop_csv, Route_csv):
    colnames_stops = ['Id','name','latitude','longitude']
    data_stops = pandas.read_csv(Stop_csv, delimiter=';', names=colnames_stops)
    #----------- Get the data of csv file with all possible stops
    stop_id = data_stops.Id.tolist()
    stop_name = data_stops.name.tolist()
    stop_latitude = data_stops.latitude.tolist()
    stop_longitude = data_stops.longitude.tolist()
    # delete first element because it is the header
    del stop_id[0]
    del stop_name[0]
    del stop_latitude [0]
    del stop_longitude [0]
    # fit in right type
    stop_id = list(map(int,stop_id))
    stop_longitude = list(map(float,stop_longitude))
    stop_latitude = list(map(float,stop_latitude))


    # --------- Get the data of csv file with all routes
    colnames_route = ['Id','Driver','Date','Req_time','Customer','Location','Fare','Estimated_time','Action','Disability']
    data_routes = pandas.read_csv(Route_csv, delimiter=';', names=colnames_route)

    route_id = data_routes.Id.tolist()
    route_driver = data_routes.Driver.tolist()
    route_date = data_routes.Date.tolist()
    route_required_time = data_routes.Req_time.tolist()
    route_customer = data_routes.Customer.tolist()
    route_location = data_routes.Location.tolist()
    route_fare = data_routes.Fare.tolist()
    route_estimated_time = data_routes.Estimated_time.tolist()
    route_action = data_routes.Action.tolist()
    route_disability = data_routes.Disability.tolist()
    # delete first row because it is the header
    del route_id[0]
    del route_driver[0]
    del route_date[0]
    del route_required_time[0]
    del route_customer[0]
    del route_location[0]
    del route_fare[0]
    del route_estimated_time[0]
    del route_action[0]
    del route_disability[0]
    # Put in right format
    route_id = list(map(int,route_id))
    route_fare = list(map(int,route_fare))




    # Date times into regular dates (2020-01-20), times into regular times

    adaptive_factor = 10  # Adapt requiered time to resemble real dataset (-10 Minutes is ok)

    for i in range(len(route_date)):
        route_date[i] = dt.datetime.strptime(route_date[i],'%d.%m.%Y').date()
    for i in range(len(route_required_time)):
        if type(route_required_time[i]) == str:
            time  = dt.datetime.strptime(route_required_time[i],'%H:%M').time()
            route_required_time[i]  = time.hour*60 + time.minute - adaptive_factor
        else:
            route_required_time[i] = 'empty'
    for i in range(len(route_estimated_time)):
        if type(route_estimated_time[i]) == str:
            time  = dt.datetime.strptime(route_estimated_time[i],'%H:%M').time()
            route_estimated_time[i] = time.hour*60 + time.minute
            route_estimated_time[i] = route_estimated_time[i]
        else:
            route_estimated_time[i] = 'empty'

    # Get all the stops, which were visited in the route dataset and store only those nodes
    matching_pairs = []
    unmatching_pairs = []
    unmatching_id = []
    fitted_route_ids = []
    for i in range(len(route_location)):
        if route_location[i] in stop_name:
            matching_pairs.append(route_location[i])
            index_id = stop_name.index(route_location[i])
            fitted_route_ids.append(stop_id[index_id])
        else:
            fitted_route_ids.append(0)
    #unmatching_pairs_unique = list(dict.fromkeys(unmatching_pairs))
    matching_pairs_unique = list(dict.fromkeys(matching_pairs))
    fitted_route_ids_unique = list(dict.fromkeys(fitted_route_ids))
    if 0 in fitted_route_ids_unique:
        fitted_route_ids_unique.remove(0)
    route_coords = []
    route_lat = []
    route_long = []
    for i in range(len(fitted_route_ids_unique)):
        index_id = stop_id.index(fitted_route_ids_unique[i])
        route_coords.append([stop_longitude[index_id],stop_latitude[index_id]])
        route_lat.append(stop_latitude[index_id])
        route_long.append(stop_longitude[index_id])
    outcome = zip(fitted_route_ids_unique,route_long,route_lat)
    """
    with open('VisitedNodesInTest.csv', "w") as f:
        writer = csv.writer(f)
        for row in outcome:
            writer.writerow(row)
    """
    #Get the customer_id from the dataset (Maria Wilke123 --> 123)
    customer_ids = []
    for i in range(len(route_customer)):
        if pandas.isnull(route_customer[i]):
            customer_ids.append(0)
        else:
            id = []
            for j in range(len(route_customer[i])):
                if route_customer[i][j].isdigit():
                    id.append(int(route_customer[i][j]))
            customer_ids.append(int("".join(map(str,id))))

    # Retrive requested route for each customer with id, origin/dest,date, requ. time, act. time: [1, [9400,9410],2020-01-20,(300,350),(298,346)]
    route_fixed = []
    route_necessary = []
    nodes = []
    time_windows_req = []
    time_windows_est = []
    for i in range(len(customer_ids)):
        if route_action[i] == 'Einstieg':
            investigated_id = customer_ids[i]
            for j in range(i+1,len(customer_ids)-1):
                if customer_ids[j] == investigated_id and route_action[j] == 'Ausstieg':
                    route_fixed.append([customer_ids[i],[str(fitted_route_ids[i]),str(fitted_route_ids[j])], route_date[i], (route_required_time[i],route_required_time[j]),(route_estimated_time[i],route_estimated_time[j])])
                    # TODO Fare einbinden --> id wichtig für später: Welche Fare konnte nicht eingesammelt werden?
                    route_necessary.append([(str(fitted_route_ids[i]),str(fitted_route_ids[j])),(route_required_time[i],route_required_time[j])])
                    nodes.append((str(fitted_route_ids[i]),str(fitted_route_ids[j])))
                    time_windows_est.append((route_estimated_time[i],route_estimated_time[j]))
                    time_windows_req.append((route_required_time[i],route_required_time[j]))
                    break
    #print(route_fixed)
    #print(route_necessary)
    return nodes, time_windows_req, time_windows_est, route_fixed, route_fare, fitted_route_ids

if __name__ == "__main__":
    stop_csv = "Stops_Krumbach.csv"
    route_csv = "KruFahrten_neu.csv"
    nodes, time_windows_req, time_windows_est, route_fixed, route_fare = ImportFLEXIBUSData(stop_csv,route_csv)
    nodes = list(itertools.chain(*nodes))
    time_windows_req = list(map(list, time_windows_req))
    time_windows_est = list(map(list, time_windows_est))
    for i in range(len(time_windows_req)):
        if time_windows_req[i][1] == 'empty':
            duration = GetMatrizes.GetDuration(nodes[2 * i], nodes[2 * i + 1])
            maximum_onb = HelpingFunctions.CalculateMaxOnBoardTime(duration)
            time_windows_req[i][1] = time_windows_req[i][0] + maximum_onb
        else:
            time_windows_req[i][0] = time_windows_req[i][0]
    time_diff_origin = []
    time_diff_destination = []
    for i in range(len(time_windows_est)):
        if time_windows_req[i][0] == 'empty':
            continue
        else:
            time_diff_origin.append(time_windows_est[i][0] - time_windows_req[i][0])
            time_diff_destination.append(time_windows_est[i][1] - time_windows_req[i][1])

    print(time_diff_destination)
    print(time_diff_origin)
    bins = [-20,-15,-10,-5,0,5,10,15,20]
    bins_small = [-10,-8,-6,-4,-2,0,2,4,6,8,10]
    bins_big = [-50,-40,-30,-20,-10,0,10,20,30]
    plt.hist(time_diff_destination, bins=bins_big, weights=np.ones(len(time_diff_destination)) / len(time_diff_destination))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.xticks(bins_big)
    plt.title("Deviation between estimated and booked arrival time")
    plt.xlabel("Deviation [min]")
    plt.ylabel("Occurrence")
    plt.show()
