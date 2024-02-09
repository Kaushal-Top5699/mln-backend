import matplotlib.pyplot as plt
import os
from wordcloud import WordCloud
from io import BytesIO
import base64

def createViz(endPath_para, clusterName_para, file_extension):
    if not os.path.exists(os.path.join(endPath_para, "visualization",f"wordCloud_{clusterName_para}_{file_extension}.html")):
        return True
    else:
        return False
    
def vcomWordCloud(lines, data):
    for i, line in enumerate(lines):
        if line.startswith('# Vertex Community File for Layer'):
            data['Layer'] = lines[i+1].strip()
        elif line.startswith('# Number of Vertices'):
            data['NumVertices'] = int(lines[i+1].strip())
        elif line.startswith('# Number of Total Communities'):
            data['NumCommunities'] = int(lines[i+1].strip())
        elif line.startswith('# Vertex Community Allocation'):
            data['Communities'] = {}
            for j in range(i+1, len(lines)):
                if not lines[j].startswith('#'):
                    vid, commID = map(int, lines[j].strip().split(','))
                    if commID in data['Communities']:
                        data['Communities'][commID].append(vid)
                    else:
                        data['Communities'][commID] = [vid]
    # print(data) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [1, 2, 3], 2: [4], 3: [5], 4: [6]}}
    return data

def ecomWordCloud(lines, data):
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
                    if commID not in data['Communities']:
                        data['Communities'][commID] = []
                    data['Communities'][commID].append((v1id, v2id))
    # print(data) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [(1,2), (2, 3), (), ...], 2: ...}}
    return data

def visualization(pathToInputFile, mln_User):
    try: 
        cluster = pathToInputFile
        input_file = f'{cluster}'
        input_file_extension = input_file.split('.')[-1]
        final_output_cluster_name = os.path.splitext(os.path.basename(input_file))[0].split('.')[0]

        if createViz(mln_User, final_output_cluster_name, input_file_extension):
            # create an empty dictionary to store the information ---------------------------------------------------------------------------------
            data = {}

            nodes_OR_edges = ""
            ecom_vcom_FLAG = ""
            uniqueNodesInEachCommunity = {}

            # read input file ---------------------------------------------------------------------------------------------------------------------
            with open(os.path.relpath(input_file), 'r') as f:
                lines = f.readlines()
            # extract vcom info from input file and store in dictionary ---------------------------------------------------------------------------
            if input_file_extension == 'vcom':
                ecom_vcom_FLAG = "vcom"
                returnData = vcomWordCloud(lines, data)
                communityData = returnData.get('Communities')  # stores data['Communities']
                nodes_OR_edges = "nodes"
            elif input_file_extension == 'ecom':
                ecom_vcom_FLAG = "ecom"
                returnData = ecomWordCloud(lines, data)
                communityData = returnData.get('Communities') # stores data['Communities']\
                nodes_OR_edges = "edges"
                # calculating unique nodes in each community --------------------------------------------------------------------------------------
                for communityID, edges in communityData.items():
                    nodes = set()
                    for edge in edges:
                        nodes.add(edge[0])
                        nodes.add(edge[1])
                    uniqueNodesInEachCommunity[communityID] = len(nodes)
                # print(uniqueNodesInEachCommunity)   # prints {1: 27, 3: 41, 2: 45} 

            # count the number of vertices in each community --------------------------------------------------------------------------------------
            verticesInEachCommunity = {'C'+str(key): len(value) if isinstance(value, list) else value for key, value in communityData.items()}
            # print(len(verticesInEachCommunity)) #{'C1': 3, 'C2': 1, 'C3': 1, 'C4': 1}

            # calculate the number of communities to display in the word cloud --------------------------------------------------------------------
            coms_to_display = min(10, len(verticesInEachCommunity))

            # create word cloud -------------------------------------------------------------------------------------------------------------------
            wordcloud = WordCloud(
                width=500,
                height=500,
                background_color='black',
                colormap='hsv',
                collocations=False,
                min_font_size=10
            )

            # generate based on the number of vertices in each community --------------------------------------------------------------------------
            wordcloud.generate_from_frequencies(verticesInEachCommunity)

            # # plot the word cloud -----------------------------------------------------------------------------------------------------------------
            # Create a subplot with two rows and one column
            fig, (ax1,ax2)= plt.subplots(1, 2, figsize=(14, 6))

            # Plot the word cloud in the first subplot
            ax1.imshow(wordcloud, interpolation="bilinear", aspect='auto')
            # Set the title for the first subplot
            ax1.set_title('Word Cloud for ' + returnData.get('Layer') + ' Layer', fontsize=16, fontweight='bold', pad=3)
            ax1.axis('off')

            # Add a legend to the second subplot -----------------------------------------------------------------------------------------------
            legent_text = f"Total Communities in {returnData.get('Layer')} Layer: {returnData.get('NumCommunities')}\n"
            if len(verticesInEachCommunity) > 10:
                legent_text += f"Top 10 Communities in {returnData.get('Layer')} Layer:\n"
            else:
                legent_text += f"All communities in {returnData.get('Layer')} Layer:\n"
            if ecom_vcom_FLAG == "vcom":
                legent_text += f"\n".join([f"{key}: {value} {nodes_OR_edges}" for key, value in sorted(verticesInEachCommunity.items(), key=lambda item: item[1], reverse=True)[:coms_to_display]])
            elif ecom_vcom_FLAG == "ecom":
                # join to legent text to print the following C1(communityID): 100(number of nodes) nodes, 200(number of edges) edges
                commmunit_legent_text = []

                for communityID, nodes_count in sorted(uniqueNodesInEachCommunity.items(), key=lambda item: item[1], reverse=True)[:coms_to_display]:
                    edges_count = verticesInEachCommunity.get('C'+str(communityID))

                    # calculate the avergae density of each community if nodes is more than 0 else the value is 0
                    ecom_average_degree = (2 * edges_count) / (nodes_count if nodes_count > 0 else 0)
                    ecom_density = (2 * edges_count) / (nodes_count * (nodes_count - 1) if nodes_count > 1 else 0)

                    commmunit_legent_text.append(f"C{communityID}: {nodes_count} nodes, {edges_count} edges, {ecom_average_degree:.2f} average degree, {ecom_density:.2f} density")
                legent_text += "\n".join(commmunit_legent_text)

            

            ax2.text(0, 1, legent_text, fontsize=12, va = 'top', ha = 'left', multialignment ='left')
            # Adjust the layout of the subplots
            fig.tight_layout(w_pad=-1)
            ax2.axis("off")
            # plt.show()

            # saving the word cloud as HTML file --------------------------------------------------------------------------------------------------
            endPath = os.path.relpath(mln_User)
            layerName = data['Layer']
            tmpfile = BytesIO()
            fig.savefig(tmpfile, format='png')
            encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

            htmlFile = f''+'<img src=\'data:image/png;base64,{}\'>'.format(encoded)+''
            with open(os.path.join(endPath,"visualization",f"wordCloud_{layerName}_{input_file_extension}.html"), "w") as f:
                f.write(htmlFile)
            return os.path.join(mln_User, "visualization",f"wordCloud_{layerName}_{input_file_extension}.html")
            # saving the word cloud as PNG file ---------------------------------------------------------------------------------------------------
            # wordcloud.to_file(os.path.join(endPath, f"{layerName}{input_file_extension}_wordCloud.png"))
        else:
            return os.path.join(mln_User, "visualization",f"wordCloud_{final_output_cluster_name}_{input_file_extension}.html")
    except Exception as e:
        print(e)
        return False