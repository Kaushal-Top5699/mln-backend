import os
import networkx as nx
from bokeh.io import show
from bokeh.plotting import figure, from_networkx, save
from bokeh.models import MultiLine, Circle, ColumnDataSource, HoverTool

def visualization(pathToInputFile, mln_User):
    cluster = pathToInputFile
    visualization_type = "G_CommunityNetwork"
    input_file = f'{cluster}'
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
                    # node1, node2, communityId = lines[j].strip().split(',')
                    G.add_node(v1id, community=commID)
                    G.add_node(v2id, community=commID)
                    G.add_edge(v1id, v2id)
                    if commID not in data['Communities']:
                        data['Communities'][commID] = []
                    data['Communities'][commID].append((v1id, v2id))
    # print(data['Communities']) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [1, 2, 3], 2: [4], 3: [5], 4: [6]}}

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
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'grey']
    for community, node_list in data['Communities'].items():
        for edge in node_list:
            G.add_edge(edge[0], edge[1])

    pos = nx.spring_layout(G)

    # bokeh --------------------------------------------------------------------------------------------------------------------------------
    title = f"{data['Layer']} Community Network Visualization"
    hover = HoverTool(tooltips=[("Node ID : ", "@index"), ('Degree : ', '@degree'),('Community : ', '@community')])
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    # HOVER_TOOLTIPS = [("Node ID : ", "@index")]
    fig = figure(
            # tooltips = HOVER_TOOLTIPS,
            tools=TOOLS,
            active_scroll='wheel_zoom',
            x_range=(-1.1,1.1), y_range=(-1.1,1.1),
            title=title,
            sizing_mode="stretch_both"
    )
    fig.title.text_font_size = '20pt'

    # Add the edges
    edge_attrs = {'line_width': 1, 'line_alpha': 0.7}
    edge_renderer = from_networkx(G, pos, scale=1, center=(0,0))
    edge_renderer.node_renderer.glyph = Circle(size=15, fill_color='gray')
    edge_renderer.edge_renderer.glyph = MultiLine(line_color='gray', **edge_attrs)
    fig.renderers.append(edge_renderer)

    # Add the nodes
    node_attrs = {'size': 20, 'fill_color': 'gray'}
    node_renderer = from_networkx(G, pos, scale=1, center=(0,0))
    node_renderer.node_renderer.glyph = Circle(**node_attrs)
    fig.renderers.append(node_renderer)

    # Add the labels
    labels = {}
    for node in G.nodes():
        labels[node] = str(node)
    nx.set_node_attributes(G, labels, 'label')
    # labels = nx.get_node_attributes(G, 'label')
    x, y = zip(*pos.values())
    node_labels = list(labels.values())
    source = ColumnDataSource({'x': x, 'y': y, 'node_labels': node_labels})
    labels_renderer = fig.text(x='x', y='y', text='node_labels', text_font_size="12pt",
                            text_align='center', text_baseline='middle', source=source)
    fig.renderers.append(labels_renderer)
    # show(fig)

    # save bokeh plo
    endPath = os.path.relpath(mln_User)
    save(fig, os.path.join(endPath,'visualization',f"bokeh_{data['Layer']}_comNet.html"), title=f"{data['Layer']} Community Network", resources='inline')
    fpath = os.path.join(mln_User,'visualization',f"bokeh_{data['Layer']}_comNet.html")
    return fpath
