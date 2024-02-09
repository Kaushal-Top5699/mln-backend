import operator
import os
import networkx as nx
import igraph as ig
from copy import deepcopy
import time
from igraph import *

# *************************** CREATES NX GRAPH ****************************************************
def create_nx_Graph(Graphfile):
    # create the networkx graph function from networkx package as this is the input for louvain
    G = nx.Graph()
    edges = []

    with open(Graphfile) as file:
        for line in file:
            # Skip comments
            if not line.startswith('#'):
                value = line.split(",")
                # read lines that are for edges (Node1, Node2, Edge Weight)
                if len(value) >= 2:
                    edges.append((int(value[0]) - 1, int(value[1]) - 1))
                    try:
                        G.add_edge(value[0], value[1],
                                   weight=float(value[2].strip()))
                    except:
                        G.add_edge(value[0], value[1], weight=float(1.0))

    # G is the graph object in networkx package format. edges is a list of all the edges in the graph which we need when writing results for edges in communities
    return G, edges

# *************************** CREATES IG GRAPH ****************************************************
def create_ig_Graph(GraphFile):
    g = ig.Graph()

    # list containing all the edge weights in order since igraph add edge method doesnt take edgeweight
    edgeWeights = []
    edges = []

    with open(GraphFile) as file:
        # skip first line since it is usually graph name (DirectorGenre, ActorGenre, etc)
        next(file)
        # add as last vertex in graph since igraph reads nodes from 0
        g.add_vertices(int(file.readline()))

        for line in file:
            value = line.split(",")
            if len(value) >= 2:
                edges.append((int(value[0]) - 1, int(value[1]) - 1))
                # append edge weight to list
                try:
                    edgeWeights.append(float(value[2]))
                except:
                    edgeWeights.append(float(1.0))

    g.add_edges(edges)

    # g is the graph object in igraph package format. edges is a list of all the edges in the graph which we need when writing results for edges in communities
    # edgeWeights is a seperate list of edgeWeights with the same length as number of vertices of the graph that the community detection algorithm takes.
    return g, edges, edgeWeights

# *************************** LOUVAIN *************************************************************
def writeResultsLouvain(result, path, edges, analysisNAME, numNodes, userName, gen_configFile_name):
    # Function to write results with Louvain result format

    if gen_configFile_name != "":
        gen_configFile_name = gen_configFile_name+"_"

    vcom_file_path = os.path.join(path, userName+"_"+gen_configFile_name+analysisNAME + ".vcom")
    ecom_file_path = os.path.join(path, userName+"_"+gen_configFile_name+analysisNAME + ".ecom")

    # Check if the .vcom file exists
    # if not os.path.exists(vcom_file_path):
        # Write the .vcom file
    with open(os.path.join(path+"/" + userName+"_"+gen_configFile_name+analysisNAME+".vcom"), 'w') as f:
        numCommunities = max(result.values()) + 1

        f.write("# Vertex Community File for Layer\n")
        f.write(analysisNAME + "\n")
        f.write("# Number of Vertices\n")
        f.write(str(numNodes) + "\n")
        f.write("# Number of Total Communities\n")
        f.write(str(numCommunities) + "\n")
        f.write("# Vertex Community Allocation: vid,commID (in sorted order of vertex IDs)\n")
        for key, value in sorted(result.items(), key=operator.itemgetter(0)):
            f.write('%s,%s\n' % (key, value + 1))

    # Check if the .ecom file exists
    # if not os.path.exists(ecom_file_path):
    # Write the .ecom file
    with open(os.path.join(path+"/" + userName+"_"+gen_configFile_name+analysisNAME+".ecom"), 'w') as f2:
        numCommunityEdges = sum(1 for edge in edges if result[edge[0]] == result[edge[1]])

        f2.write("# Edge Community File for Layer\n")
        f2.write(analysisNAME + "\n")
        f2.write("# Number of Vertices\n")
        f2.write(str(numNodes) + "\n")
        f2.write("# Number of Non-Singleton Communities\n")
        f2.write(str(numCommunities) + "\n")
        f2.write("# Number of Edges in Communities\n")
        f2.write(str(numCommunityEdges) + "\n")
        f2.write("# Edge Community Allocation: v1,v2,commID (sorted by vid1, then vid2)\n")
        for edge in edges:
            if result[edge[0]] == result[edge[1]]:
                f2.write('%s,%s,%s\n' % (edge[0], edge[1], result[edge[0]] + 1))

# *************************** INFOMAP *************************************************************
def writeResultsInfomap(infomap, path, edges, analysisNAME, userName, gen_configFile_name):
    # Function to write results with infomap result format
    # result is in im.modules which we can iterate through like this
    # for node_id, module_id in infomap.modules: (here module_id is the same as community_id)
    # if not os.path.exists(path):
    #     os.makedirs(path)
    # infomap.write_clu(os.path.join(path+"/"+analysisNAME+".clu"))
    
    if gen_configFile_name != "":
        gen_configFile_name = gen_configFile_name+"_"

    # WRITING ECOM FILE FOR INFOMAP ***************************************************************
    currentCommunity = 0
    communityList = []
    # t0 = time.time()

    vcom_file_path = os.path.join(path, userName+"_"+gen_configFile_name+analysisNAME + ".vcom")
    ecom_file_path = os.path.join(path, userName+"_"+gen_configFile_name+analysisNAME + ".ecom")
    
    # Check if the .vcom file exists
    # if not os.path.exists(vcom_file_path):
    # Write the .vcom file
    with open(os.path.join(path+"/"+ userName+"_"+gen_configFile_name+analysisNAME + ".vcom"), 'w') as f:
        numCommunities = 0
        numNodes = 0
        for node_id, module_id in infomap.modules:
            if module_id > numCommunities:
                numCommunities = module_id
            if node_id > numNodes:
                numNodes = node_id

        f.write("# Vertex Community File for Layer\n")
        f.write(analysisNAME + "\n")
        f.write("# Number of Vertices\n")
        f.write(str(numNodes) + "\n")
        f.write("# Number of Total Communities\n")
        f.write(str(numCommunities) + "\n")
        f.write("# Vertex Community Allocation: vid,commID (in sorted order of vertex IDs)\n")

        for node_id, module_id in infomap.modules:
            if module_id != currentCommunity:
                communityList.append([])
                currentCommunity = module_id
            if len(communityList) > module_id - 1:
                communityList[module_id - 1].append(node_id)
            f.write('%s,%s\n' % (node_id, module_id))

    # WRITING ECOM FILE FOR INFOMAP ***************************************************************
    # Check if the .ecom file exists
    # if not os.path.exists(ecom_file_path):
    # Write the .ecom file
    communityBridgeEdges = deepcopy(edges)
    count = 0
    # t1 = time.time() - t0
    # t2 = time.time()
    # Extract community information
    communities = []
    for node_id, module_id in infomap.modules:
        while module_id >= len(communities):
            communities.append([])
        communities[module_id].append(node_id)

    # Count non-singleton communities
    numSingletonCommunities = 0
    for community in communities:
        if len(community) > 1:
            numSingletonCommunities += 1

    # Count edges in communities
    numCommunityEdges = 0
    
    for index, community in enumerate(communities):
        community_edges = set()
        for edge in edges:
            if edge[0] in community and edge[1] in community:
                community_edges.add((edge[0], edge[1]))
        numCommunityEdges += len(community_edges)

    # Write edges and the community they are in
    with open(os.path.join(path+"/"+userName+"_"+gen_configFile_name+analysisNAME+".ecom"), 'w') as f2:
        numNodes = len(infomap.modules)
        numCommunities = len(communities)

        f2.write("# Edge Community File for Layer\n")
        f2.write(analysisNAME + "\n")
        f2.write("# Number of Vertices\n")
        f2.write(str(numNodes) + "\n")
        f2.write("# Number of Non-Singleton Communities\n")
        f2.write(str(numSingletonCommunities + 1) + "\n")
        f2.write("# Number of Edges in Communities\n")
        f2.write(str(numCommunityEdges) + "\n")
        f2.write("# Edge Community Allocation: v1,v2,commID (sorted by vid1, then vid2)\n")

        for i, edge in enumerate(edges):
            for index, community in enumerate(communities):
                if edge[0] in community and edge[1] in community:
                    f2.write('%s,%s,%s\n' % (edge[0], edge[1], index))
                    communityBridgeEdges.pop(i - count)
                    count += 1

        # Write singleton communities
        for i, node in enumerate(range(1, numNodes + 1)):
            node_in_communities = False
            for community in communities:
                if node in community:
                    node_in_communities = True
                    break
            if not node_in_communities:
                f2.write('%s,%s,%s\n' % (node, node, numCommunities + i + 1))

        # Write the non-singleton node as a separate community
        f2.write('%s,%s,%s\n' % (numNodes, numNodes, numSingletonCommunities + 1))


# *************************** FASTGREEDY | WALKTRAP | LEADIGNEIGENVECTOR | MULTILEVEL **************************
def writeResults(result, path, edges, analysisNAME, algo, t, numNodes, userName, gen_configFile_name):
    
    if gen_configFile_name != "":
        gen_configFile_name = gen_configFile_name+"_"

    vcom_file_path = os.path.join(path, userName+"_"+gen_configFile_name+analysisNAME + ".vcom")
    ecom_file_path = os.path.join(path, userName+"_"+gen_configFile_name+analysisNAME + ".ecom")

    numCommunities = len(result)

    # Check if the .vcom file exists
    # if not os.path.exists(vcom_file_path):
    # Write the .vcom file
    with open(os.path.join(path+"/"+userName+"_"+gen_configFile_name+analysisNAME+".vcom"), 'w') as f:
        f.write("# Vertex Community File for Layer\n")
        f.write(analysisNAME + "\n")
        f.write("# Number of Vertices\n")
        f.write(str(numNodes) + "\n")
        f.write("# Number of Total Communities\n")
        f.write(str(numCommunities) + "\n")
        f.write("# Vertex Community Allocation: vid,commID (in sorted order of vertex IDs)\n")
        # f.write("#Time taken "+t+"s\n")
        
        for index, community in enumerate(result):
            for node in community:
                f.write('%s,%s\n' % (node+1, index+1))
    
    # Check if the .ecom file exists
    # if not os.path.exists(ecom_file_path):
    # Write the .ecom file
    communityBridgeEdges = deepcopy(edges)
    count = 0
    # t1 = time.time() - t0
    # t2 = time.time()

    # calculate the # of edges in communities
    numCommunityEdges = 0
    for i, edge in enumerate(edges):
        for index, community in enumerate(result):
            if edge[0] in community and edge[1] in community:
                numCommunityEdges += 1

    with open(os.path.join(path+"/"+userName+"_"+gen_configFile_name+analysisNAME+".ecom"), 'w') as f:
        f.write("# Edge Community File for Layer\n")
        f.write(analysisNAME + "\n")
        f.write("# Number of Vertices\n")
        f.write(str(numNodes) + "\n")
        f.write("# Number of Non-Singleton Communities\n")
        f.write(str(numCommunities) + "\n")
        f.write("# Number of Edges in Communities\n")
        f.write(str(numCommunityEdges) + "\n")
        f.write("# Edge Community Allocation: v1,v2,commID (sorted by vid1, then vid2)\n")
        # f.write("#Time taken " + t + "s\n")
        for i, edge in enumerate(edges):
            for index, community in enumerate(result):
                if edge[0] in community and edge[1] in community:
                    f.write('%s,%s,%s\n' % (edge[0]+1, edge[1]+1, index + 1))
                    communityBridgeEdges.pop(i - count)
                    count += 1

def createVertexClusteringObjectLouvain(partition, graphLocation):

    # create a VertexClusteringObject for louvain dictionary since comparision format is a VCO
    igG, _, _ = create_ig_Graph(graphLocation)
    igG.add_vertex(0)

    membership = [None] * (igG.vcount())

    for node_id, community_id in partition.items():
        index = int(node_id)
        membership[index] = int(community_id)

    m = max(partition.values()) + 1

    # membership is a list which contains all community_IDs of the graph
    # example [0,0,0,1,1,1]
    # here nodes 0,1,2 are in community 0 and nodes 3,4,5 are in community 1 (vertices count of graph should match membership length)
    for val in range(len(membership)):
        if membership[val] is None:
            membership[val] = m
            m += 1

    # inbuilt igraph function to create a vertex_clustering_object with ig.graph and membership list as parameters
    return ig.VertexClustering(igG, membership=membership)

def createVertexClusteringObjectInfomap(im, graphLocation):

    # create a VertexClusteringObject for infomap object since comparision format is a VCO
    igG, _, _ = create_ig_Graph(graphLocation)
    igG.add_vertex(0)

    membership = [None] * (igG.vcount())
    m = 0

    for node_id, module_id in im.modules:
        if module_id - 1 > m:
            m = module_id - 1
        index = int(node_id)
        membership[index] = int(module_id - 1)

    # membership is a list which contains all community_IDs of the graph
    # example [0,0,0,1,1,1]
    # here nodes 0,1,2 are in community 0 and nodes 3,4,5 are in community 1 (vertices count of graph should match membership length)
    for val in range(len(membership)):
        if membership[val] is None:
            membership[val] = m
            m += 1

    # inbuilt igraph function to create a vertex_clustering_object with ig.graph and membership list as parameters
    return ig.VertexClustering(igG, membership=membership)
