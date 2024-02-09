import networkx as nx
import os
import plotly.graph_objects as go

def get_files_names():
    data_dir = 'data'
    file_names = []
    for file in os.listdir(data_dir):
        if file.endswith('.txt') or file.endswith('.net'):
            file_names.append(file)
            # print(file) #prints file names with .txt
    return file_names

def visualization(pathToInputFile, mln_User,mappingfile):
    cluster = pathToInputFile
    visualization_type = "graph"
    input_file = f'{cluster}'
    output_file_cluster_name = cluster.split('/')[-1]
    output_file = f'visualization_{visualization_type}_{output_file_cluster_name}.html'
    print(mappingfile)
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
        # print(allEdges[0]) # prints node1, node2, weight(1.0)

    mapper=[]
    with open(os.path.relpath(mappingfile),"r") as fi:
        for line in fi.readlines()[1:]:
            cur_line=line.split(",")
            mapper.append(",".join(cur_line[1:]))
        

    # CREATE GRAPH -----------------------------------------------------------------------
    G = nx.Graph()
    for edge in allEdges:
        G.add_edge(edge[0], edge[1], weight=edge[2])

    # define position for nodes in the graph ---------------------------------------------
    pos = nx.kamada_kawai_layout(G)
    pos = {node: (x, y) for node, (x, y) in pos.items()}
    edge_pos = {(u, v): pos[u] for u, v in G.edges()}
    nx.set_edge_attributes(G, edge_pos, 'pos')

    # CREATE BLANK PLOTLY FIGURE ---------------------------------------------------------
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[],
        y=[]
    ))

    # CREATE EDGES EDGE_TRACE ------------------------------------------------------------
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        if 'weight' not in edge[2]:
            edge[2]['weight'] = 1.0
        edge_trace = go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines',
            line=dict(width=edge[2]['weight'],color='#202213'),
            hoverinfo='none',
            showlegend=False
        )
        fig.add_trace(edge_trace)

    # CREATE NODES NODE_TRACE ------------------------------------------------------------
    node_x = []
    node_y = []
    node_text = []
    # node_color = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        # node_text.append(str(node))
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            showscale=True,
            colorscale='rainbow',
            reversescale=True,
            color=[],
            size=14,
            colorbar=dict(
                thickness=15,
                title='Node Connections/ Degree Centrality',
                xanchor='left',
                titleside='right'
            ),
            line_width=2
        ),
        text=node_text,
        showlegend=True,
        hovertext=node_text,
        hoverinfo='text'
                        )

    # COLOR NODE POINTS TEXT -------------------------------------------------------------
    node_adjacencies = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('Node ID: ' + str(mapper[node-1]) + '<br />Degree Centrality: '+ str(len(adjacencies[1])))
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    fig.add_trace(node_trace)

    # CREATE LAYOUT ----------------------------------------------------------------------
    layout = go.Layout(
            title=f'<br />Network graph for {clusterName.upper()} layer',
            titlefont_size=16,
            legend_title_text=f"Nodes: {len(G.nodes)} | Edges: {len(G.edges)}",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    # UPATE FIGURE -----------------------------------------------------------------------
    fig.update_layout(layout)
    # fig.show()

    # SAVE FIGURE ------------------------------------------------------------------------
    endPath = os.path.relpath(mln_User)
    clusterName = clusterName.split('.')[0] # remove the .txt extension
    fig.write_html(os.path.join(endPath,'visualization',f"{clusterName}_network.html"))
    fpath=os.path.join(mln_User,'visualization',f"{clusterName}_network.html")
    return fpath
