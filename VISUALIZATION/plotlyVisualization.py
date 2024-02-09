import networkx as nx
import os
from prometheus_client import generate_latest
from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objects as go
import webbrowser
# import mpld3
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg')

allNodes = []
# fileName = "American.txt" # input file name


def get_files_names():
    data_dir = 'data'
    file_names = []
    for file in os.listdir(data_dir):
        if file.endswith('.txt') or file.endswith('.net'):
            file_names.append(file)
            # print(file) #prints file names with .txt
    return file_names


# adjust the size of nodes
# add ondes or circles
def generate_figures(G, pos, clusterName, mln_User):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[],
        y=[]
    ))
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        if 'weight' not in edge[2]:
            edge[2]['weight'] = 1.0
        fig.add_trace(go.Scatter(x=[x0, x1, None], y=[y0, y1, None],
                                 mode='lines', line=dict(width=edge[2]['weight'], color='black')))
    # Add node labels
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(str(node))
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text', text=node_text,
                             textfont=dict(size=10), showlegend=False))
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, b=20, t=20))
    # fig.write_image(os.path.join('static', clusterName + '_network.svg'))
    #print(endPath)
    endPath = os.path.relpath(mln_User)
    cluserName=clusterName.split('.')[0]
    fig.write_html(os.path.join(endPath,'visualization',f"{cluserName}_network.html"))
    
    #file_path=os.path.join(mln_User,'visualization',f"{cluserName}_network.html")
    #webbrowser.open_new_tab(f'file:///{file_path}')
    #webbrowser.open('http://bangkok.uta.edu/mlndash-test/'+file_path,new=2)
    fpath=os.path.join(mln_User,'visualization',f"{cluserName}_network.html")
    return fpath

def networkVis(clusterName, G, mln_User):
    pos = nx.kamada_kawai_layout(G)
    return generate_figures(G, pos, clusterName, mln_User)


def visualization(pathToInputFile, mln_User):
    cluster = pathToInputFile
    visualization_type = "graph"
    # visualization_type = request.form['visualization_type']
    input_file = f'{cluster}'
    output_file_cluster_name = cluster.split('/')[-1]
    print("OP file name",output_file_cluster_name)
    output_file = f'visualization_{visualization_type}_{output_file_cluster_name}.html'
    # check if output file already exists, and return it if it does
    if os.path.exists(os.path.join('static', output_file)):
        return send_file(output_file, mimetype='image/svg+xml/html/png')
    # read data from file
    # f = open("American1.txt", "r")
    # with open(os.path.join('data', input_file), "r") as f:
    
    with open(os.path.relpath(input_file), "r") as f:
        print(os.path.relpath(input_file))
        allLines = f.readlines()
        clusterName = allLines[0].strip()
        noVerticesLayer1 = allLines[1].strip()
        noVerticesLayer2 = allLines[2].strip()
        x = int(noVerticesLayer1) + int(3)  # print 293
        # nodes = f.readline()[x:]  # nodes in the format <node_1, node_2, weight>
        f.seek(0)  # reset the file pointer to the beginning of the file
        for line in f.readlines()[x:]:
            line = line.strip()
            nodes = line.split(',')
            allNodes.append((nodes[0], nodes[1], float(nodes[2])))
        print(clusterName)
        print(noVerticesLayer1)
        print(noVerticesLayer2)
        # print(allNodes)  # prints list of tuples "[(x,y,1.0),(...),(...]"
    # create graph
    G = nx.Graph()
    for nodes in allNodes:
        node1, node2, weight = nodes
        G.add_weighted_edges_from([(node1, node2, weight)])
    # generate visualization
    if visualization_type == 'graph':
        return networkVis(output_file_cluster_name, G, mln_User)

