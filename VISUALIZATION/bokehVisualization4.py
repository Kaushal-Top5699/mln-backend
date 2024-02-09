import networkx as nx
import os
from bokeh.io import show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Viridis8, Spectral8
from networkx.algorithms import community as comm

def createViz(endPath_para, clusterName_para):
    # print(os.path.join(endPath_para,f"bokeh_{clusterName_para}_Network.html"))
    if not os.path.exists(os.path.join(endPath_para,"visualization",f"bokeh_{clusterName_para}_Network.html")):
        return True
    else:
        return False

def visualization(pathToInputFile, mappingInputFile , mln_User):
    cluster = pathToInputFile
    input_map_file = f'{mappingInputFile}'
    input_file = f'{cluster}'
    output_file_cluster_name = cluster.split('/')[-1]
    final_output_cluster_name = output_file_cluster_name.split('.')[0].strip()
    endPath = os.path.relpath(mln_User)

    # check if we need to create viz or load generated viz
    # if True, create viz and save it
    if createViz(mln_User, final_output_cluster_name):
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
            # print(allEdges) # prints node1, node2, weight(1.0)

        mapper = []
        with open(os.path.relpath(input_map_file), "r") as fi:
            for line in fi.readlines():
                cur_lin = line.strip().split(',')
                mapper.append(",".join(cur_lin[1:]))
        # print(mapper[1:]) #prints from ABR...

        G = nx.Graph()
        for node_list in allEdges:
            G.add_node(node_list[0])
            G.add_node(node_list[1])
        for node_list in allEdges:
            G.add_edge(node_list[0], node_list[1], weight=node_list[2])

        # add labels to nodes ---------------------------------------------------------------
        labels = {}
        for node in G.nodes():
            labels[node] = mapper[int(node)]
            # print(labels[node])
        # print(labels.get('51')) #prints ORD
        nx.set_node_attributes(G, labels, "label")

        # BOKEH ------------------------------------------------------------------------------
        # Calculate degree for each node and add as node attribute ---------------------------
        degrees = dict(nx.degree(G))
        nx.set_node_attributes(G, name='degree', values=degrees)

        # Set node size based on degree ----------------------------------------------------
        num_to_adjust_by = 5
        adjusted_node_size = dict([(node, degree+num_to_adjust_by) for node, degree in nx.degree(G)])
        nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

        # calculate Communities --------------------------------------------------------------
        communities = comm.greedy_modularity_communities(G)

        # Add modularity class as node attribute ----------------------------------------------
        modularity_class = {}
        modularity_color = {}
        for community_number, community in enumerate(communities):
            # For each member of the community, add their community number and a distinct color
            for name in community:
                modularity_class[name] = community_number
                modularity_color[name] = Spectral8[community_number]
        nx.set_node_attributes(G, name='modularity_class', values=modularity_class)
        nx.set_node_attributes(G, name='modularity_color', values=modularity_color)

        # Create data source for nodes and edges ---------------------------------------------
        node_data = dict(
            index=list(G.nodes()),
            degree= list(dict(G.degree()).values()),
            labels=list(nx.get_node_attributes(G, 'label').values()),
            modularity_class=list(nx.get_node_attributes(G, 'modularity_class').values()),
        )
        source = ColumnDataSource(node_data)

        #Choose colors for node and edge highlighting
        node_highlight_color = 'white'
        edge_highlight_color = 'black'

        size_by_this_attribute = 'adjusted_node_size'
        color_by_this_attribute = 'modularity_color'
        color_palette = Viridis8

        # Title of the graph -----------------------------------------------------------------
        title = f"{clusterName} Network Graph"
        # Hovering over the nodes ------------------------------------------------------------
        HOVER_TOOLTIPS = [
            ("Node Label", "@label"),
            ("# of Connections", "@degree"),
            ("Modularity Class", "@modularity_class"),
        ]

        # create plot and style it -----------------------------------------------------------
        plot = figure(
            tooltips = HOVER_TOOLTIPS,
            tools = "pan,wheel_zoom,box_zoom,reset,save",
            active_scroll = "wheel_zoom",
            title = title,
            x_range = Range1d(-10, 10), y_range = Range1d(-10, 10),
            sizing_mode="stretch_both" # autoresize
        )
        plot.title.text_font_size = '20pt'

        network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

        #Set node sizes and colors according to node degree (color as category from attribute)
        network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=color_by_this_attribute)
        network_graph.node_renderer.data_source.data.update(source.data)
        #Set node highlight colors
        network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
        network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

        #Set edge opacity and width
        network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
        #Set edge highlight colors
        network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

        #Highlight nodes and edges
        network_graph.selection_policy = NodesAndLinkedEdges()
        network_graph.inspection_policy = NodesAndLinkedEdges()

        plot.renderers.append(network_graph)

        # show(plot)
        # SAVE FIGURE ------------------------------------------------------------------------
        save(plot, os.path.join(endPath, "visualization",f"bokeh_{clusterName}_Network.html"), title=f"{clusterName} Network Graph", resources='inline')

        # close the file
        f.close()
        return os.path.join(mln_User, "visualization",f"bokeh_{clusterName}_Network.html")
    else:
        return os.path.join(mln_User, "visualization",f"bokeh_{final_output_cluster_name}_Network.html")
