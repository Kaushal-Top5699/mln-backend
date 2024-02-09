from pyvis.network import Network
import os
import networkx as nx

def createViz(endPath_para, clusterName_para):
    if not os.path.exists(os.path.join( endPath_para,"visualization",f"pyvis_{clusterName_para}_Network.html")):
        return True
    else:
        return False

def visualization(pathToInputFile,mln_User):
    cluster = pathToInputFile
    output_file_cluster_name = cluster.split('/')[-1]
    final_output_cluster_name = output_file_cluster_name.split('.')[0].strip() # remove the .txt extension
    input_file = f'{cluster}'
    endPath = os.path.relpath(mln_User)

    # check if we need to create viz or load generated viz
    # if True, create viz and save it
    if createViz(mln_User, final_output_cluster_name):

        # creating the network graph layout
        result_net = Network(
            font_color="yellow",
            width="100%",
            height="100vh",    # vh is view port height
            bgcolor="#222222",
            # heading=f"Network Graph for {final_output_cluster_name}", # ALERT: this prints the heading twice BUG
            # neighborhood_highlight=True,  # ALERT: turning this on will not disappear the loading bar at all. BUG
            # filter_menu=True,
        )
        #setting physics layout of the network
        result_net.force_atlas_2based(spring_length=100)

        # reading the input file
        allEdges = []
        with open(os.path.relpath(input_file), "r") as f:
            allLines = f.readlines()
            clusterName = allLines[0].strip()
            noVerticesLayer1 = allLines[1].strip()
            noVerticesLayer2 = allLines[2].strip()
            x = int(noVerticesLayer1) + int(3)  # print 293
            f.seek(0)  # reset the file pointer to the beginning of the file
            for line in f.readlines()[x:]:
                node1, node2, weigth = line.strip().split(',')
                allEdges.append((node1, node2, float(weigth)))
                # adding nodes and edges into graph
        for node1,node2,weigth in allEdges:
            result_net.add_node(node1, title = node1, border_width = 5, borderWidthSelected = 10, color = {'background': 'white', 'border': 'magenta'})
            result_net.add_node(node2, title = node2, border_width = 5, borderWidthSelected = 10, color = {'background': 'white', 'border': 'magenta'})
            result_net.add_edge(node1, node2, value = weigth, color = {'color': 'cyan', 'highlight': 'pink', 'hover': 'yellow'})

        neighbor_map = result_net.get_adj_list()

        for node in result_net.nodes:
            node["title"] += " adjacent nodes:\n" + "\n".join(neighbor_map[node["id"]])
            node["value"] = len(neighbor_map[node["id"]])

        result_net.toggle_hide_edges_on_drag(False)
        # result_net.toggle_physics(False)
        result_net.set_edge_smooth("dynamic")
        result_net.show_buttons(filter_=['physics'])
        result_net.show(os.path.join(endPath, "visualization",f"pyvis_{clusterName}_Network.html"))
        f.close()
        return os.path.join(mln_User, "visualization", f"pyvis_{clusterName}_Network.html")
    else:
        return os.path.join(mln_User, "visualization", f"pyvis_{final_output_cluster_name}_Network.html")
