# bokehApp.py

import holoviews as hv
import numpy as np

import holoviews.operation.datashader as hd
import datashader as ds
from holoviews.operation.datashader import datashade, dynspread
from datashader.colors import Sets1to3
import pandas as pd

from bokeh.io import show
from bokeh.layouts import layout, gridplot
from bokeh.models import Slider, Button, AutocompleteInput, Label, Select
from bokeh.plotting import curdoc

import math

import colorcet as cc

import sys
from pymongo import MongoClient

df = pd.read_csv('../../textfilesv2/umap.txt', delimiter=' ')
df2 = pd.read_csv('../../textfilesv2/metadata.txt', delimiter=' ')

df3 = pd.read_csv('../../textfilesmicroglia/umap.txt', delimiter=' ')
df4 = pd.read_csv('../../textfilesmicroglia/metadata.txt', delimiter=' ')

cstring = sys.argv[1]
client = MongoClient(cstring)
db=client.admin

hv.extension('bokeh', 'matplotlib')
renderer = hv.renderer('bokeh').instance(mode='server')


def getGenes():
    return db.genesfullv2.distinct('name')

def getVals(gene):
    query = db.genesfullv2.find({'name' : gene})
    
    temp = {}
    for doc in query: #for each doc in query, get the value dictionary
        temp = doc['values']

    arr = np.zeros(346264, dtype=int)
    for key in temp:

        arr[int(key)] = 1

    return arr

def getGenes_microglia():
    return db.genesfullmicroglia.distinct('name')

def getVals_microglia(gene):
    query = db.genesfullmicroglia.find({'name' : gene})
    
    temp = {}
    for doc in query: #for each doc in query, get the value dictionary
        temp = doc['values']

    arr = np.zeros(17089, dtype=int)
    for key in temp:
        arr[int(key)] = 1


    return arr

def basegraph(gene, set):
	#print(gene)
	if (set == "all"):
		return hv.Points((df["UMAP_1"], df["UMAP_2"], getVals(gene)), ['UMAP_1', 'UMAP_2'], vdims='Category')
	elif (set == "microglia"):
		return hv.Points((df3["UMAP_1"], df3["UMAP_2"], getVals_microglia(gene)), ['UMAP_1', 'UMAP_2'], vdims='Category')

def fullgraph(set):
	if (set == "all"):
		return hv.Points((df["UMAP_1"], df["UMAP_2"], df2["SCT_snn_res.0.2"]), ['UMAP_1', 'UMAP_2'], vdims='Category')
	elif (set == "microglia"):
		return hv.Points((df3["UMAP_1"], df3["UMAP_2"], df4["SCT_snn_res.0.2"]), ['UMAP_1', 'UMAP_2'], vdims='Category')


stream = hv.streams.Stream.define('Gene', gene="", set="all")()
streamSet = hv.streams.Stream.define('Set', set="all")()


dmap = dynspread(datashade(hv.DynamicMap(basegraph, streams=[stream]), aggregator=ds.count_cat('Category'), color_key=['#c9c9c9', '#00008a']).opts(plot=dict(width=600, height=450)))


dmap_full = dynspread(datashade(hv.DynamicMap(fullgraph, streams=[streamSet]), aggregator=ds.count_cat('Category'), color_key=Sets1to3).opts(plot=dict(width=600, height=450)))

def modify_doc(doc):

	def ac_update(attrname, old, new):
		stream.event(gene=new)
		print(ac.value)

	def dd_update(attrname, old, new):
		streamSet.event(set=new)
		stream.event(set=new)
		print(dd.value)

	dd = Select(title="Cell Set", value="all",
                   options=['all', 'microglia'])
	ac = AutocompleteInput(title="Type in a gene and select from the dropdown", value="", completions=getGenes())

	dd.on_change('value', dd_update)
	ac.on_change('value', ac_update)

	hvplot = renderer.get_plot(dmap, doc)
	hvplot_full = renderer.get_plot(dmap_full, doc)

	plot = gridplot([[ac, dd], [hvplot.state, hvplot_full.state]])

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