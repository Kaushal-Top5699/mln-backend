import mpld3
import matplotlib.pyplot as plt
import os
from wordcloud import WordCloud
import matplotlib.patches as mpatches
import plotly.graph_objects as go


def visualization(pathToInputFile, mln_User):
    cluster = pathToInputFile
    visualization_type = "wordCloud"
    input_file = f'{cluster}'
    input_file_extension = input_file.split('.')[-1]
    inputFileNameWOExtension = os.path.splitext(
        os.path.basename(input_file))[0]
    output_file = f'{inputFileNameWOExtension}{input_file_extension}_wordCloud.html'
    # TODO: check if the visualization for the output files already exists

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
        communityData = returnData.get('Communities') # stores data['Communities']

    # count the number of vertices in each community --------------------------------------------------------------------------------------
    verticesInEachCommunity = {'c'+str(key).strip(): len(value) if isinstance(
        value, list) else value for key, value in communityData.items()}
    # print(verticesInEachCommunity) #{'C1': 3, 'C2': 1, 'C3': 1, 'C4': 1}
    # create word cloud -------------------------------------------------------------------------------------------------------------------
    wordcloud = WordCloud(width=500, height=500, max_words=200, background_color="black")
    # generate based on the number of vertices in each community --------------------------------------------------------------------------
    wordcloud.generate_from_frequencies(verticesInEachCommunity)

    # plot the word cloud -----------------------------------------------------------------------------------------------------------------
    plt.figure(figsize=(5, 5),facecolor=None)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)

    # saving the word cloud as HTML file --------------------------------------------------------------------------------------------------
    endPath = os.path.relpath(mln_User)
    layerName = data['Layer']
    htmlFile = mpld3.fig_to_html(plt.gcf())
    with open(os.path.join(endPath,'visualization',f"{layerName}{input_file_extension}_wordCloud.html"), "w") as f:
        f.write(htmlFile)
    # saving the word cloud as PNG file ---------------------------------------------------------------------------------------------------
    wordcloud.to_file(os.path.join(endPath,'visualization',f"{layerName}{input_file_extension}_wordCloud.png"))
    fpath=os.path.join(mln_User,'visualization',f"{layerName}{input_file_extension}_wordCloud.html")
    return fpath
    #plt.show()

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
    # print(data) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [1, 2, 3], 2: [4], 3: [5], 4: [6]}}
    return data
