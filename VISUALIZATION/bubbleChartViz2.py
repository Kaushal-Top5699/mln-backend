import codecs
import os
from matplotlib import pyplot as plt
import pandas as pd
import circlify
from io import BytesIO
import base64

def createViz(endPath_para, clusterName_para, file_extension):
    if not os.path.exists(os.path.join(endPath_para,"visualization",f"circlepacking_{clusterName_para}_{file_extension}.html")):
        return True
    else:
        return False

def visualization(pathToInputFile, mln_user):
    cluster = pathToInputFile
    input_file = f'{cluster}'
    input_file_extension = input_file.split('.')[-1]
    final_output_cluster_name = os.path.splitext(os.path.basename(input_file))[0].split('.')[0]

    # check if the file already exists
    if createViz(mln_user, final_output_cluster_name, input_file_extension):
        # create an empty dictionary to store the information ---------------------------------------------------------------------------------
        data = {}
        # read input file ---------------------------------------------------------------------------------------------------------------------
        with open(os.path.relpath(input_file), 'r') as f:
            lines = f.readlines()
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

        verticesInEachCommunity = {'c'+str(key).strip(): len(value) if isinstance(
            value, list) else value for key, value in data['Communities'].items()}
        # print(verticesInEachCommunity) #{'1': 3, '2': 1, '3': 1, '4': 1}

        # matplotlib ----------------------------------------------------------------------------------------------------------------------------
        comNames = []
        comSizes = []
        for key, value in verticesInEachCommunity.items():
            comNames.append(key)
            comSizes.append(value)
        df = pd.DataFrame({'Name': comNames, 'Value': comSizes})
        df = df.sort_values(by=['Value'])

        circles = circlify.circlify(
            (df['Value']).tolist(),
            show_enclosure=False,
            target_enclosure=circlify.Circle(x=0, y=0, r=1)
        )

        fig,ax = plt.subplots(figsize=(10,10), facecolor='#fff')
        ax.set_title('Circular packing of '+ str(data['Layer']) +' communities', fontsize=20, fontweight='bold')
        ax.axis('off')
        ax.set_aspect('equal') # sshow circles as circles and not as ellipses
        lim = max(
            max(
                abs(circle.x) + circle.r,
                abs(circle.y) + circle.r
            )
            for circle in circles
        )
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)

        labels = list(df['Name'])

        for circle,label in zip(circles,labels):
            x, y, r = circle
            ax.add_patch(plt.Circle((x, y), r, linewidth = 2, facecolor='#AE183D', edgecolor='yellow'))
            font_size = r*150 # adjust font size based on circle size
            plt.annotate(
                label,
                (x,y ) ,
                va='center',
                ha='center',
                fontsize=font_size,
                color = 'white',
            )
        # makes the extra white-space in the figure to be removed and largens the figure
        plt.tight_layout()

        # saving the word cloud as HTML file --------------------------------------------------------------------------------------------------
        endPath = os.path.relpath(mln_user)
        layerName = data['Layer']
        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        htmlFile = f''+'<img src=\'data:image/png;base64,{}\'>'.format(encoded)+''
        with open(os.path.join(endPath,"visualization",f"circlepacking_{layerName}_{input_file_extension}.html"), "w") as f:
            f.write(htmlFile)
        return os.path.join(mln_user,"visualization",f"circlepacking_{layerName}_{input_file_extension}.html")
    else:
        return os.path.join(mln_user,"visualization",f"circlepacking_{final_output_cluster_name}_{input_file_extension}.html")