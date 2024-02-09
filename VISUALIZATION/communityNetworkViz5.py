import os
import networkx as nx
from bokeh.io import show
from bokeh.plotting import figure, from_networkx, save
from bokeh.palettes import Viridis256
from bokeh.models import MultiLine, Circle, ColumnDataSource, LinearColorMapper, ColorBar, Legend, LegendItem
from networkx.algorithms import community as comm
import itertools
import re

def createViz(endPath_para, clusterName_para):
    if not os.path.exists(os.path.join(endPath_para, "visualization",f"bokeh_{clusterName_para}_comNet.html")):
        return True
    else:
        return False

def visualization(pathToInputFile, mappingInputFile, mln_User):
    try:
        cluster = pathToInputFile
        input_file = f'{cluster}'
        # get the input file name from the path (if path/to/file/southwest_louvain.ecom gets southwest_louvain)
        inputFile_base_name = os.path.basename(input_file).split('.')[0]
        endPath = os.path.relpath(mln_User)
        final_output_cluster_name = os.path.splitext(os.path.basename(input_file))[0].split('.')[0]

        # Defining a regex pattern for the specified endings
        ending_pattern = r"_louvain|_infomap|_fastgreedy|_walktrap|_multilevel|_leadingeigenvector"
        # Using regex to remove the specified ending
        final_output_cluster_name = re.sub(ending_pattern, "", inputFile_base_name)

        # checking if mapping file exists
        input_map_file_path = f'{mappingInputFile}'
        # join the mapping file to path
        input_map_file =  os.path.join(input_map_file_path, f'{final_output_cluster_name}.map')
        mappingFile_present = os.path.exists(input_map_file)
        print(f"Mapping file present: {mappingFile_present}")

        if createViz(mln_User, final_output_cluster_name):
            # dictionary to maintain the data
            data = {}
            G = nx.Graph()
            # read input file ---------------------------------------------------------------------------------------------------------------------
            with open(os.path.relpath(input_file), 'r') as f:
                lines = f.readlines()
            # extract vcom info from input file and store in dictionary
            for i, line in enumerate(lines):
                if line.startswith('# Edge Community File for Layer'):
                    data['Layer'] = lines[i+1].strip()
                elif line.startswith('# Number of Vertices'):
                    data['NumVertices'] = int(lines[i+1].strip())
                elif line.startswith('# Number of Non-Singleton Communities'):
                    data['NumCommunities'] = int(lines[i+1].strip())
                elif line.startswith('# Number of Community Edges'):
                    data['NumCommunitiesEdges'] = int(lines[i+1].strip())
                elif line.startswith('# Edge Community Allocation'):
                    data['Communities'] = {}
                    for j in range(i+1, len(lines)):
                        if not lines[j].startswith('#'):
                            v1id, v2id, commID = map(int, lines[j].strip().split(','))
                            G.add_node(v1id, community=commID)
                            G.add_node(v2id, community=commID)
                            G.add_edge(v1id, v2id)
                            if commID not in data['Communities']:
                                data['Communities'][commID] = []
                            data['Communities'][commID].append((v1id, v2id))
            # print(data['Communities']) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [1, 2, 3], 2: [4], 3: [5], 4: [6]}}

            # create mapper
            mapper = []
            if mappingFile_present:
                with open(os.path.relpath(input_map_file), "r") as fi:
                    for line in fi.readlines():
                        cur_lin = line.strip().split(',')
                        mapper.append(",".join(cur_lin[1:]))
                # print(mapper[5]) #prints from ABR...

            community_list = []
            node_list = []
            for community, node in data['Communities'].items():
                community_list.append(community)
                node_list.append(node)

            G = nx.Graph()

            for node_list in data['Communities'].values():
                for edge in node_list:
                    G.add_node(edge[0])
                    G.add_node(edge[1])
            for community, node_list in data['Communities'].items():
                for edge in node_list:
                    G.add_edge(edge[0], edge[1])

            # calculate degree of each node
            degrees = dict(nx.degree(G))
            nx.set_node_attributes(G, name='degree', values=degrees)

            # Set node size based on degree ----------------------------------------------------
            num_to_adjust_by = 5
            adjusted_node_size = dict([(node, degree+num_to_adjust_by) for node, degree in nx.degree(G)])
            nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

            communities = comm.greedy_modularity_communities(G)

            modularity_class = {}
            modularity_color = {}
            for community_number, community in enumerate(communities):
                # For each member of the community, add their community number and a distinct color
                for name in community:
                    modularity_class[name] = community_number
                    # modularity_color[name] = Viridis256[community_number]
            # create a color mapper to assign colors to each community
            palette = Viridis256
            palette_length = len(palette)
            color_mapper = LinearColorMapper(palette=palette,
                                            low=min(modularity_class.values()),
                                            high=max(modularity_class.values()),
                                            nan_color="#CCCCCC")
            # create a color iterator for cycling through the colors in the palette
            color_iterator = itertools.cycle(palette)
            for name, community_number in modularity_class.items():
                index = community_number % palette_length
                modularity_color[name] = color_mapper.palette[index]

            nx.set_node_attributes(G, name='modularity_class', values=modularity_class)
            nx.set_node_attributes(G, name='modularity_color', values=modularity_color)

            # add labels to nodes ---------------------------------------------------------------
            labels = {}
            for node in G.nodes():
                if mappingFile_present:
                    labels[node] = mapper[int(node)]
                else:
                    labels[node] = node
            nx.set_node_attributes(G, labels, "label")

            # Create data source for nodes and edges ---------------------------------------------
            node_data = dict(
                index=list(G.nodes()),
                degree= list(dict(G.degree()).values()),
                labels=list(nx.get_node_attributes(G, 'label').values()),
                modularity_class=list(nx.get_node_attributes(G, 'modularity_class').values()),
            )
            source = ColumnDataSource(node_data)
            from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges
            #Choose colors for node and edge highlighting
            node_highlight_color = 'white'
            edge_highlight_color = 'black'

            size_by_this_attribute = 'adjusted_node_size'
            color_by_this_attribute = 'modularity_color'

            # bokeh --------------------------------------------------------------------------------------------------------------------------------
            title = f"{data['Layer']} Community Network Visualization"
            TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
            HOVER_TOOLTIPS = [("Node ID : ", "@index"), ("Label : ", "@label"), ('Degree : ', '@degree'),('Community : ', '@modularity_class')]
            fig = figure(
                    tooltips = HOVER_TOOLTIPS,
                    tools=TOOLS,
                    active_scroll='wheel_zoom',
                    x_range=(-10,10), y_range=(-10,10),
                    title=title,
                    sizing_mode="stretch_both" # autoresize
            )
            fig.title.text_font_size = '20pt'


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

            # Legend --------------------------------------------------------------------------------------------------------------------------------
            legend = Legend(items=[
                LegendItem(label=f"Total Number of Communities : {data['NumCommunities']}", renderers=[network_graph.node_renderer]),
            ], location="top_left")
            fig.add_layout(legend)

            # add color bar --------------------------------------------------------------------------------------------------------------------------
            color_bar = ColorBar(color_mapper=color_mapper, label_standoff=0, border_line_color=None, location=(0, 0))
            fig.add_layout(color_bar, 'right')

            fig.renderers.append(network_graph)

            # save bokeh plot
            save(fig, os.path.join(endPath,"visualization",f"bokeh_{data['Layer']}_comNet.html"), title=f"{data['Layer']} Community Network", resources='inline')
            return os.path.join(mln_User,"visualization",f"bokeh_{data['Layer']}_comNet.html")
        else:
            return os.path.join(mln_User,"visualization",f"bokeh_{final_output_cluster_name}_comNet.html")
    except Exception as e:
        print(str(e))
        return False