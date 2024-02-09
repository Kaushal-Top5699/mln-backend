import networkx as nx
import os
from bokeh.io import show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LinearColorMapper
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Turbo256, Viridis256, Spectral8, Purples256, Blues256, Greens256, Oranges256
from networkx.algorithms import community as comm

def createViz(endPath_para, clusterName_para):
    # print(os.path.join(endPath_para,f"bokeh_{clusterName_para}_Network.html"))
    if not os.path.exists(os.path.join(endPath_para,"visualization",f"bokeh_{clusterName_para}_Network.html")):
        return True
    else:
        return True
        # return False
    
"""
    This function reads the input .net file and returns a list of tuples of all the edges
    and the number of vertices in each layer

    Parameters:
        inputFile: path to the input .net file

    Returns:    
        allEdges: list of tuples of all the edges
        clusterName: name of the cluster
        noVerticesLayer1: number of vertices in layer 1
        noVerticesLayer2: number of vertices in layer 2
"""
def readingFile(inputFile):
    allEdges = []
    with open(os.path.relpath(inputFile), "r") as f:
        allLines = f.readlines()
        clusterName = allLines[0].strip()
        noVerticesLayer1 = allLines[1].strip()
        noVerticesLayer2 = allLines[2].strip()
        x = int(noVerticesLayer1) + int(3)  # print 293
        f.seek(0)  # reset the file pointer to the beginning of the file
        for line in f.readlines()[x:]:
            node1, node2, weigth = line.strip().split(',')
            allEdges.append((node1, node2, float(weigth)))
    # close the file
    f.close()

    return allEdges, clusterName, noVerticesLayer1, noVerticesLayer2

"""
    This function creates a bokeh visualization of the input .net file

    Parameters:
        pathToInputFile: path to the input .net file
        mappingInputFile: path to the mapping file
        mln_User: path to the user directory

    Returns:
        path to the bokeh visualization file
"""
def visualization(pathToInputFile, mappingInputFile , mln_User):
    # try:
        cluster = pathToInputFile
        input_file = f'{cluster}'
        # get the input file name from the path (if path/to/file/southwest.net gets southwest)
        inputFile_base_name = os.path.basename(input_file).split('.')[0]
        output_file_cluster_name = cluster.split('/')[-1]
        final_output_cluster_name = output_file_cluster_name.split('.')[0].strip()
        endPath = os.path.relpath(mln_User)

        # checking if mapping file exists
        input_map_file_path = f'{mappingInputFile}'
        # join the mapping file to path
        mappingFile_present = os.path.exists(input_map_file_path)
        print(f"Mapping file present: {mappingFile_present}")

        # check if we need to create viz or load generated viz
        # if True, create viz and save it
        if createViz(mln_User, final_output_cluster_name):
            
            # function that reads the input .net file
            allEdges, clusterName, noVerticesLayer1, noEdges_fromFile = readingFile(input_file)
            
            # create mapper
            mapper = []
            if mappingFile_present:
                with open(os.path.relpath(input_map_file_path), "r") as fi:
                    for line in fi.readlines():
                        cur_lin = line.strip().split(',')
                        mapper.append(",".join(cur_lin[1:]))
                # print(mapper[1:]) #prints from ABR...

            # assign a scale according to the number of nodes
            if int(noEdges_fromFile) > 1100 and int(noEdges_fromFile) < 3000:
                custom_scale = 12
            elif int(noEdges_fromFile) > 3000 and int(noEdges_fromFile) < 6000:
                custom_scale = 14
            elif int(noEdges_fromFile) > 6000 and int(noEdges_fromFile) < 10000:
                custom_scale = 16
            else:
                custom_scale = 10

            
            # Check if there are no edges
            if int(noEdges_fromFile) == 0:
                # Create a graph with only nodes
                G = nx.Graph()
                for node in range(int(noVerticesLayer1)):
                    G.add_node(node)

                # Add labels to nodes if needed
                labels = {}
                if mappingFile_present:
                    for node in range(int(noVerticesLayer1)):
                        labels[node] = mapper[node]
                else:
                    for node in range(int(noVerticesLayer1)):
                        labels[node] = str(node)

                nx.set_node_attributes(G, labels, "label")

                # Create data source for nodes
                node_data = dict(
                    index=list(G.nodes()),
                    labels=list(nx.get_node_attributes(G, 'label').values()),
                )
                source = ColumnDataSource(node_data)

                #Choose colors for node and edge highlighting
                node_highlight_color = 'white'  
                size_by_this_attribute = 'adjusted_node_size'          

                # Title of the graph -----------------------------------------------------------------
                title = f"{clusterName} Network Graph"
                # Hovering over the nodes ------------------------------------------------------------
                HOVER_TOOLTIPS = [
                    ("Node Label", "@label"),
                ]

                # Create the plot for nodes only
                plot = figure(
                    tooltips=HOVER_TOOLTIPS,
                    tools="pan,wheel_zoom,box_zoom,reset,save",
                    active_scroll="wheel_zoom",
                    title=title,
                    x_range=Range1d(-10, 10),
                    y_range=Range1d(-10, 10),
                    sizing_mode="stretch_both"  # autoresize
                )
                plot.title.text_font_size = '20pt'

                # Render and style nodes
                network_graph = from_networkx(G, nx.spring_layout, scale=custom_scale, center=(0, 0))
                network_graph.node_renderer.glyph = Circle()
                print(source.data)
                network_graph.node_renderer.data_source.data.update(source.data)
                network_graph.node_renderer.hover_glyph = Circle(fill_color=node_highlight_color, line_width=2)
                network_graph.node_renderer.selection_glyph = Circle(fill_color=node_highlight_color, line_width=2)

                plot.renderers.append(network_graph)

                # Save the figure
                save(plot, os.path.join(endPath, "visualization", f"bokeh_{clusterName}_Network.html"), title=f"{clusterName} Network Graph", resources='inline')

                return os.path.join(mln_User, "visualization", f"bokeh_{clusterName}_Network.html")
            # if therr are edges
            else:
                G = nx.Graph()
                for node_list in allEdges:
                    G.add_node(int(node_list[0]))
                    G.add_node(int(node_list[1]))
                for node_list in allEdges:
                    G.add_edge(int(node_list[0]), int(node_list[1]), weight=node_list[2])

                # add labels to nodes ---------------------------------------------------------------
                labels = {}
                for node in G.nodes():
                    if mappingFile_present:
                        labels[node] = mapper[int(node)]
                    else:
                        labels[node] = node
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
                        try:
                            modularity_color[name] = Spectral8[community_number]
                        except:
                            try:
                                modularity_color[name] = Viridis256[community_number]
                            except:
                                try:
                                    modularity_color[name] = Turbo256[community_number]
                                except:
                                    try:
                                        modularity_color[name] = Purples256[community_number]
                                    except:
                                        try:
                                            modularity_color[name] = Blues256[community_number]
                                        except:
                                            try:
                                                modularity_color[name] = Greens256[community_number]
                                            except:
                                                try:
                                                    modularity_class[name] = Oranges256[community_number]
                                                except:
                                                    modularity_color[name] = 'blue'


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

                # size_by_this_attribute = 'adjusted_node_size'
                color_by_this_attribute = 'modularity_color'

                # Title of the graph -----------------------------------------------------------------
                title = f"{clusterName} Network Graph using Louvain Community Detection"
                # Hovering over the nodes ------------------------------------------------------------
                HOVER_TOOLTIPS = [
                    ("Node Label", "@label"),
                    ("Connections", "@degree"),
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

                # fix to the bokeh graph error ------------------------------------------------------
                mappinggg = dict((n, i) for i, n in enumerate(G.nodes()))
                H = nx.relabel_nodes(G, mappinggg)

                # Render and style nodes --------------------------------------------------------------
                try:
                    network_graph = from_networkx(G, nx.spring_layout, scale=custom_scale, center=(0, 0))
                except:
                    try:
                        network_graph = from_networkx(H, nx.spring_layout, scale=custom_scale, center=(0, 0))
                    except Exception as e:
                        print(f"ERROR occured for bokeh visualization: {e}")

                size_by_this_attribute = 20

                #Set node sizes and colors according to node degree (color as category from attribute)
                network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=color_by_this_attribute)
                network_graph.node_renderer.data_source.data.update(source.data)
                # Set node highlight colors
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
                save(plot, os.path.join(endPath, "visualization",f"bokeh_{clusterName}_Network.html"), title=f"{clusterName} Network Graph using Louvain Community Detection", resources='inline')

                return os.path.join(mln_User, "visualization",f"bokeh_{clusterName}_Network.html")
        else:
            return os.path.join(mln_User, "visualization",f"bokeh_{final_output_cluster_name}_Network.html")
    # except Exception as e:
    #     print(f"ERROR occured for bokeh visualization: {e}")