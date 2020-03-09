# bokehApp.py

import holoviews as hv
import numpy as np

import holoviews.operation.datashader as hd
import datashader as ds
from holoviews.operation.datashader import datashade, dynspread
from datashader.colors import Sets1to3
import pandas as pd

from bokeh.io import show
from bokeh.layouts import layout
from bokeh.models import Slider, Button, AutocompleteInput
from bokeh.plotting import curdoc

from bokeh.palettes import Blues4

import colorcet as cc

import sys
from pymongo import MongoClient

#for i in range(0, len(sys.argv)):
#	print(i)
#	print(sys.argv[i])
#	print("--------------")
numColors = 1

df = pd.read_csv('../textfiles/umap.txt', delimiter=' ')
df2 = pd.read_csv('../textfiles/metadata.txt', delimiter=' ')

cstring = sys.argv[1]
client = MongoClient(cstring)
db=client.admin

hv.extension('bokeh', 'matplotlib')
renderer = hv.renderer('bokeh').instance(mode='server')

def getGenes():
    return db.genesfull.distinct('name')

def getVals(gene):
    x = db.genesfull.find({'name' : gene})
    
    temp = {}
    for doc in x:
        temp = doc['values']
        
    arr = np.zeros(336295, dtype=int)
    for key in temp:
        #arr[int(key)] = temp.get(key)
        arr[int(key)] = 1

    numColors = len(set(arr))
    print(numColors)
    return arr

def basegraph(gene):
	print(gene)
	return hv.Points((df["UMAP_1"], df["UMAP_2"], getVals(gene)), ['UMAP_1', 'UMAP_2'], vdims='Category')

print(cc.fire[:10])

stream = hv.streams.Stream.define('Gene', gene="")()

#categorical_points = hv.Points((df["UMAP_1"], df["UMAP_2"], df2["SCT_snn_res.0.2"]), ['UMAP_1', 'UMAP_2'], vdims='Category')
#cc.blues
dmap = dynspread(datashade(hv.DynamicMap(basegraph, streams=[stream]), aggregator=ds.count_cat('Category'), color_key=Sets1to3).opts(plot=dict(width=600, height=450)))
#ds = datashade(dmap, aggregator=ds.count_cat('Category'), color_key=Sets1to3).opts(plot=dict(width=600, height=45))

#dmap = dynspread(datashade(categorical_points, aggregator=ds.count_cat('Category'), color_key=Sets1to3).opts(plot=dict(width=600, height=450)), streams=[stream])

#dmap = hv.DynamicMap(graph, streams=[stream])


def modify_doc(doc):

	def ac_update(attrname, old, new):
		stream.event(gene=new)
		#print(ac.value)

	ac = AutocompleteInput(title="Type in a gene and select from the dropdown", value="", completions=getGenes())
	ac.on_change('value', ac_update)

	hvplot = renderer.get_plot(dmap, doc)
	plot = layout([[ac], [hvplot.state]])
	doc.add_root(plot)
# To display in a script
doc = modify_doc(curdoc())


















    #categorical_points = hv.Points((df["UMAP_1"], df["UMAP_2"], df2["SCT_snn_res.0.2"]), ['UMAP_1', 'UMAP_2'], vdims='Category')

    #dmap = dynspread(datashade(categorical_points, aggregator=ds.count_cat('Category'), color_key=Sets1to3).opts(plot=dict(width=600, height=450)))

    #app = renderer.app(dmap)
    #server = Server({'/': app}, port=8050, allow_websocket_origin=["fenix.psych.wucon.wustl.edu:5001"]) #####################
    #server.start()
    #loop = IOLoop.current()
    #loop.start()