import random
import ALNS_parallel
import ALNS_Regret
import ALNS_Regret3

def InsertNodes (route_list, demand_pass ,time_window, mydict, unfitting_nodes,removed_nodelist, weighing_insertion, number_insertion, demand_pack):
    # Insert a the removed nodes in the routes using a specific insertion heuristic
    if len(number_insertion) == 3:
        selected_method = random.choices([0,1,2],weights=weighing_insertion,k=1)
    if len(number_insertion) == 2:          # Regret-3-heuristic not possible because only 2 routes
        selected_method = random.choices([0, 1,], weights=weighing_insertion, k=1)
    number_insertion[selected_method[0]] += 1           # count the amount of times the heuristics have been used
    id_insertion = selected_method[0]                   # id of the selected mehtod
    if selected_method[0] == 0:
        route_list, unfitting_nodes = ALNS_parallel.ALNS_Recursion(route_list, demand_pass, demand_pack, time_window, mydict, unfitting_nodes, removed_nodelist)
    if selected_method[0] == 1:
        route_list, unfitting_nodes = ALNS_Regret.RegretHeuristic(route_list,demand_pass, demand_pack, time_window, mydict, unfitting_nodes, removed_nodelist)
    if selected_method[0] == 2:
        route_list, unfitting_nodes = ALNS_Regret3.RegretHeuristic(route_list, demand_pass, demand_pack, time_window, mydict, unfitting_nodes, removed_nodelist)
    return route_list, unfitting_nodes, id_insertion, number_insertion
