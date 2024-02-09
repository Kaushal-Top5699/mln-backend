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

def visualization(pathToInputFile, mln_User):
    cluster = pathToInputFile
    input_file = f'{cluster}'
    input_file_extension = input_file.split('.')[-1]
    final_output_cluster_name = os.path.splitext(os.path.basename(input_file))[0].split('.')[0]
    # print("final_output_cluster_name: ", final_output_cluster_name)       # prints ActorGenre

    if createViz(mln_User, final_output_cluster_name, input_file_extension):
        # create an empty dictionary to store the information ---------------------------------------------------------------------------------
        data = {}
        # read input file ---------------------------------------------------------------------------------------------------------------------
        with open(os.path.relpath(input_file), 'r') as f:
            lines = f.readlines()
        # extract vcom info from input file and store in dictionary ---------------------------------------------------------------------------
        if input_file_extension == 'vcom':
            returnData = vcomWordCloud(lines, data)
            communityData = returnData.get('Communities')  # stores data['Communities']
        elif input_file_extension == 'ecom':
            returnData = ecomWordCloud(lines, data)
            communityData = returnData.get('Communities') # stores data['Communities']\

        # count the number of vertices in each community --------------------------------------------------------------------------------------
        verticesInEachCommunity = {'C'+str(key): len(value) if isinstance(value, list) else value for key, value in communityData.items()}
        # print(verticesInEachCommunity) #{'C1': 3, 'C2': 1, 'C3': 1, 'C4': 1}

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

        # Add a legend to the second subplot
        legent_text = f"Total Communities in {returnData.get('Layer')} Layer: {returnData.get('NumCommunities')}\nTop 10 Communities in {returnData.get('Layer')} Layer:\n" + "\n".join([f"C{key}: {value}" for key, value in sorted(verticesInEachCommunity.items(), key=lambda item: item[1], reverse=True)[:10]])
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
    #print(data['Layer']) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [1, 2, 3], 2: [4], 3: [5], 4: [6]}}
    #data['Layer'] = 'ABC'
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
    # print(data) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [1, 2, 3], 2: [4], 3: [5], 4: [6]}}
    return data
