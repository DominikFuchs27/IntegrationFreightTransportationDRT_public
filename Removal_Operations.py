import random
import Testing_RandomRemoval
import Testing_WorstRemoval
import Testing_Relatedeness

def RemoveNodes(Mainroute,route_list,degree_of_deconstruction, nodelist, weighing_removal, number_removal):
    # Select removal heuristic to remove a certain set of nodes from the routes
    selected_method = random.choices([0,1,2],weights=weighing_removal,k=1)
    if sum(number_removal) == 0:
        selected_method = [0]                   # Prevent that it is "worst removal" in first step --> no schedule yet for invehicle-time
    number_removal[selected_method[0]] += 1     # count amount of times a heuristic have been chosen
    id_removal = selected_method[0]
    if selected_method[0] == 0:
        removed_nodelist, indexes = Testing_RandomRemoval.RandomRemoval(nodelist,degree_of_deconstruction)
    elif selected_method[0] == 1:
        removed_nodelist, indexes = Testing_Relatedeness.ShawRemoval(Mainroute,nodelist,degree_of_deconstruction)
    elif selected_method[0] == 2:
        removed_nodelist, indexes = Testing_WorstRemoval.WorstRemoval(route_list,degree_of_deconstruction,nodelist)
    return removed_nodelist, indexes, id_removal, number_removal
