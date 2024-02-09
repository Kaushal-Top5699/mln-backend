# import networkx as nx
# import matplotlib.pyplot as plt
# import linecache as lc
# import plotly.graph_objects as go

# # --------------------------------------------
# # METHOD #1 : NETWORKX and matPlotLib

# # reading the data
# # G = nx.read_edgelist("Bridge_Edges.txt", create_using=nx.Graph(), nodetype=int)
# # print(G)
# # # drawing the graph
# # pos = nx.spring_layout(G)
# # nx.draw_networkx_nodes(G, pos)
# # nx.draw_networkx_edges(G, pos)
# # plt.show()


# # --------------------------------------------
# # METHOD #2 : Using networkX and matplotlib

# # creating a graph
# G = nx.Graph()

# # creating a edge list tuple to store all the edges
# edgeList = []

# # # adding edges
# fileName = "Bridge_Edges.txt"
# with open(fileName) as f:
#     for line in f:
#         if(line[0].isnumeric()):
#             # (node1, node2) = line.split(',')
#             # edgeList.append(lc.getline(r"Bridge_Edges.txt", i))
#             edgeList.append(line)
#             print(edgeList)
#         else:
#             continue
#     # print(G.edges.data("weight", default=1))

# # i = 0
# # for (edgess) in (edgeList):
# #     node1 = edgess[i][0]
# #     node2 = edgess[i][1]
# #     i+=1
# #     # G.add_edge(edgess[i][0], edgess[i][1], weight=edgess[i][2])
# #     G.add_edge(node1, node2)
# #     print(G.edges)


# # drawing the graph
# # nx.draw_networkx(G, with_labels = True)
# # plt.show()

# # --------------------------------------------
# # METHOD # 3: CREATING A GRAPH USING PLOTLY

# edge_x = []
# edge_y = []
# for edge in G.edges():
#     x0, y0 = G.nodes[edge[0]]
#     # x0, y0 = G.nodes[edge[0]]
#     # x1, y1 = G.nodes[edge[1]]
#     edge_x.append(x0,y0)
#     # edge_x.append(x1)
#     # edge_x.append(None)
#     # edge_y.append(y0)
#     # edge_y.append(y1)
#     # edge_y.append(None)

# edge_trace = go.Scatter(
#     x=node1, y=node2,
#     line=dict(width=0.5, color='#888'),
#     hoverinfo='none',
#     mode='lines')

# # node_x = []
# # node_y = []
# # for node in G.nodes():
# #     x, y = G.nodes[node]['pos']
# #     node_x.append(x)
# #     node_y.append(y)

# node_trace = go.Scatter(
#     # x=node_x, y=node_y,
#     x=node1, y=node2,
#     mode='markers',
#     hoverinfo='text',
#     marker=dict(
#         showscale=True,
#         # colorscale options
#         #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
#         #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
#         #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
#         colorscale='YlGnBu',
#         reversescale=True,
#         color=[],
#         size=10,
#         colorbar=dict(
#             thickness=15,
#             title='Node Connections',
#             xanchor='left',
#             titleside='right'
#         ),
#         line_width=2))

# # fig = go.Figure(data=[edge_trace, node_trace],
# fig = go.Figure(data=[edge_trace, node_trace],
#              layout=go.Layout(
#                 title='<br>Network graph made with Python',
#                 titlefont_size=16,
#                 showlegend=False,
#                 hovermode='closest',
#                 margin=dict(b=20,l=5,r=5,t=40),
#                 annotations=[ dict(
#                     text="Python code: <a href='https://plotly.com'> https://plotly.com</a>",
#                     showarrow=False,
#                     xref="paper", yref="paper",
#                     x=0.005, y=-0.002 ) ],
#                 xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#                 yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
#                 )
# fig.show()

# import linecache
# import matplotlib.pyplot as plt
# import networkx as nx

# edgeListStr = []
# f = open("American.txt", "r")

# def totalNoLines(f):
#     linesCount = sum(1 for line in f)
#     return linesCount

# for line in f:
#     if(line[0].isnumeric()):
#         edgeListStr.append(line.replace("\n",""))
#     else:
#         continue
# # print(edgeListStr)

# # [['node1','node2'],['node1','node2'],...]
# edgess = []

# for i in range(len(edgeListStr)):
#     edgess.append(edgeListStr[i].split(","))
# print(edgess)
# print(edgess[0][0])
# print(edgess[0][1])
# print(edgess[2][0])
# print(edgess[2][1])

# G = nx.Graph()
# for i in range(len(edgess)):
#     G.add_edge(edgess[i][0], edgess[i][1])
# nx.draw_networkx(G, with_labels = True)
# plt.show()


# ------------------------------------------------------------------------
# CREATING USING NETWORKX AND MATPLOTLIB
# genereates basic graph with nodes and edges, un organized, but can be saves as PNG
import os
import networkx as nx
import matplotlib.pyplot as plt

def visualizer(fileToVisualize):
    G=nx.Graph()
    f = open(os.path.relpath(fileToVisualize), "r")
    f.readline()
    number=int(f.readline())+3
    print(number)
    for line in f.readlines()[number:]:
        line = line.strip()
        nodes = line.split(',')

        G.add_edge(nodes[0], nodes[1])

    nx.draw(G, with_labels = True)
    plt.show()
    return ""

# ------------------------------------------------------------------------

# # IMPLEMENTING CYTOSCAPE
# import dash
# import dash_cytoscape as cyto
# from dash import html
# from dash import dcc
# from dash.dependencies import Input, Output
# import pandas as pd
# import plotly.express as px

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# df = open("American1.txt", "r")

# app.layout = html.Div([
#     html.Div([
#         cyto.Cytoscape(
#             id='org-chart',
#             layout={'name': 'preset'},
#             style={'width': '100%', 'height': '500px'},
#             elements=[
#                 # Nodes elements
#                 {'data': {'id': 'node1', 'label': 'node1'},
#                  'position': {'x': 150, 'y': 50},
#                  'locked': True
#                  },

#                 {'data': {'id': 'node2', 'label': 'node2'},
#                  'position': {'x': 0, 'y': 150},
#                  'grabbable': False
#                  },

#                 {'data': {'id': 'node3', 'label': 'node3'},
#                  'position': {'x': 300, 'y': 150},
#                  'selectable': False
#                  },

#                 {'data': {'id': 'node4', 'label': 'node4'},
#                  'position': {'x': -100, 'y': 250},
#                  'selected': True
#                  },

#                 {'data': {'id': 'node5', 'label': 'node5'},
#                  'position': {'x': 150, 'y': 250}
#                  },

#                 {'data': {'id': 'node6', 'label': 'node6'},
#                  'position': {'x': 300, 'y': 350}
#                  },

#                 # Edge elements
#                 {'data': {'source': 'node1', 'target': 'node1', 'label': 'node1 to node6'}},
#                 {'data': {'source': 'node2', 'target': 'node2'}},
#                 {'data': {'source': 'node3', 'target': 'node3'}},
#                 {'data': {'source': 'node4', 'target': 'node4'}},
#                 {'data': {'source': 'node5', 'target': 'node5'}},
#             ]
#         )
#     ], className='six columns'),

#     html.Div([
#         dcc.Graph(id='my-graph')
#     ], className='six columns'),

# ], className='row')


# @app.callback(
#     Output('my-graph', 'figure'),
#     Input('org-chart', 'tapNodeData'),
# )
# def update_nodes(data):
#     if data is None:
#         dff = df.copy()
#         dff.loc[dff.name == 'node1', 'color'] = "yellow"
#         fig = px.bar(dff, x='name', y='slaves_freed')
#         fig.update_traces(marker={'color': dff['color']})
#         return fig
#     else:
#         print(data)
#         dff = df.copy()
#         dff.loc[dff.name == data['label'], 'color'] = "yellow"
#         print(dff)
#         fig = px.bar(dff, x='name', y='slaves_freed')
#         fig.update_traces(marker={'color': dff['color']})
#         return fig


# if __name__ == '__main__':
#     app.run_server(debug=True)
