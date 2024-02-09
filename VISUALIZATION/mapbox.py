import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import os
import numpy as np
def visualize(configfile,mappingfile,mln_User):
    fname=configfile.split('/')[-1]
    fname=fname.split('.')[0]
    if(os.path.exists(os.path.join(mln_User,"visualization",f"{fname}_map.html"))):
        return os.path.join(mln_User,"visualization",f"{fname}_map.html")    

    us_cities = pd.read_csv(os.path.relpath(mappingfile))
    print(us_cities.head())

    np.random.seed(123)
    colors = pd.Series(np.random.choice(290, size=len(us_cities)))
    colors = colors.astype(str)
    fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon",hover_name="Airport Code" 
                            ,color_discrete_sequence=px.colors.qualitative.Set1, zoom=3,height=1080)

    with open(os.path.relpath(configfile), "r") as f:
        allLines = f.readlines()
        clusterName = allLines[0].strip()
        noVerticesLayer1 = allLines[1].strip()
        noVerticesLayer2 = allLines[2].strip()
        x = int(noVerticesLayer1) + int(3)  # print 293
        f.seek(0)  # reset the file pointer to the beginning of the file
        for line in f.readlines()[x:]:
            node1, node2, weigth = line.strip().split(',')
            fig.add_trace(
            go.Scattermapbox(
                lat=[us_cities.iloc[int(node1)-1]['lat'], us_cities.iloc[int(node2)-1]['lat']],
                lon=[us_cities.iloc[int(node1)-1]['lon'], us_cities.iloc[int(node2)-1]['lon']],
                mode='lines',
                line=dict(
                    color='black',
                    width=0.05
                ),
                hoverinfo='skip',
                showlegend=False
            ))
            
    fig.update_traces(marker=dict(size=12),
                  selector=dict(mode='markers'))
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #fig.show()
    fig.write_html(os.path.join(os.path.relpath(mln_User),"visualization",f"{fname}_map.html"))
    fpath=os.path.join(mln_User,"visualization",f"{fname}_map.html")    
    return fpath
