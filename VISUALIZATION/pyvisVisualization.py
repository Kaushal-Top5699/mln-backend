from pyvis.network import Network
import linecache,os,webbrowser

def visualization(pathToInputFile,mln_User):
    print("now running pyvis visualization ... ")
    cluster = pathToInputFile
    print(cluster)
    output_file_cluster_name = cluster.split('/')[-1]
    clusterName = output_file_cluster_name.split('.')[0] # remove the .txt extension
    input_file = f'{cluster}'

    V = int(linecache.getline(input_file,2))
    E = int(linecache.getline(input_file,3))
    idList=[]
    edgeList=[]

    #get the id's of the graph nodes vertices (V)
    for i in range(4,V+4):
        idList.append(int(linecache.getline(input_file,i)))

    #get the id's of the graph nodes vertices (E)
    for i in range(V+4,V+4+E):
        edgeList.append(linecache.getline(input_file,i))

    #get the edges i the graph
    for i in range(len(edgeList)):
        edgeList[i] = edgeList[i].replace('\n',"")

    #remove the excess data from the edge list and convert it to int
    for i in range(len(edgeList)):
        x=edgeList[i].split(",")
        x.pop()
        for j in range(len(x)):
            x[j]=int(x[j])
        edgeList[i]=x

    net = Network(bgcolor="#000000",font_color="white")
    #net.add_nodes(idList)

    for i in range(len(idList)):
        net.add_node(idList[i],label=str(idList[i]),color="red",height='100%',width='100%')

    for i in range(len(edgeList)):
        net.add_edge(edgeList[i][0],edgeList[i][1],color="blue",physics=False)

    #net.width="100%"
    #net.height="100%"
    net.show_buttons(filter_=['physics'])
    
    #net.show(os.path.join(os.path.relpath(mln_User),f"{clusterName}_PyvisNetwork.html"))
    print(mln_User)
    vis_path=os.path.join(os.path.join(os.path.relpath(mln_User),"visualization"))
    print(vis_path)
    net.save_graph(os.path.join(vis_path,f"{clusterName}_PyvisNetwork.html"))
    fpath = os.path.join(mln_User,"visualization",f"{clusterName}_PyvisNetwork.html")
    return fpath


