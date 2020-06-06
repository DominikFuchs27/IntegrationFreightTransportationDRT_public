
import random

def RandomRemoval(nodes, degree_of_deconstruction):
    # removes randomly selected nodes
    number_deleted_nodes = round(len(nodes) * degree_of_deconstruction)     # calculate number of deleted nodes
    indexes = random.sample(range(len(nodes)), number_deleted_nodes)        # get random indexes
    indexes.sort(reverse=True)          # sort the indexes in the right order
    removed_nodelist = []
    for i in range(len(indexes)):               # remove nodes from list
        node = nodes.pop(indexes[i])
        removed_nodelist.append(node)
    removed_nodelist = list(removed_nodelist)
    return removed_nodelist, indexes


