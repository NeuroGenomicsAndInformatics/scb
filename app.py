import sys
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime as dt
import pandas as pd
import plotly.graph_objs as go

from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np

import logging

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

#handler = logging.FileHandler('test500k.log')
#handler.setLevel(logging.DEBUG)

#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)

#logger.addHandler(handler)

# take db connection stirng from the commandline as an argument
cstring = sys.argv[1]
#logger.info('Sending request for database connection.')
client = MongoClient(cstring)
#logger.info('Connected.')
db=client.admin

def getGenes():
    #logger.info('Querying for all genes for dropdown...')
    x = db.genesfull.find()
    #logger.info('Done. (Querying for all genes for dropdown...)')

    #logger.info('Processing documents returned by query for all gene names...')
    geneList = []
    
    for doc in x:
        geneList.append(doc['name'])
    logger.info('Done. (Processing documents returned by query for all gene names...)')
    return geneList

def getVals(selected_dropdown_value):
    #logger.info('Querying for gene expression values...')
    x = db.genesfull.find({'name' : selected_dropdown_value})
    #logger.info('Done. (Querying for gene expression values...)')
    
    #logger.info('Processing documents returned by query for gene expression values...')
    temp = {}
    for doc in x:
        temp = doc['values']
        
    arr = np.zeros(336295, dtype=int)
    for key in temp:
        arr[int(key)] = temp.get(key)

    #logger.info('Done. (Processing documents returned by query for gene expression values...)')
    return arr

app = dash.Dash('Hello World')
#logger.info('Reading in UMAP values...')
df = pd.read_csv('umap.txt', delimiter=' ')
#logger.info('Done. (Reading in UMAP values...)')

app.layout = html.Div([
    html.Div([dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': gene, 'value': gene} for gene in getGenes()
        ],
        value=''
    )]),
    html.Div([dcc.Graph(id='my-graph')], style={'display': 'inline-block'}),
    #html.Div([html.Img(src = app.get_asset_url ('prototype.png'))], style={'display': 'inline-block', 'height': 100, 'width' : 100})
])

@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    #logger.info('Begin updating process of plot...')
    return {
            'data': [
                go.Scatter(
                    x=df["UMAP_1"],
                    y=df["UMAP_2"],
                    hoverinfo='skip',
                    mode='markers',
                    opacity=0.7,
                    marker=dict(
                        color=getVals(selected_dropdown_value),
                        size=3,
                        colorscale='OrRd',
                        colorbar=dict(thickness=10)
                    )
                )
            ],
            'layout': go.Layout(
                xaxis=dict(title='UMAP_1', showgrid=False, zeroline=False),
                yaxis=dict(title='UMAP_2', showgrid=False, zeroline=False),
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                hovermode='closest',
                height=500,
                width=600
            )
    }

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
