# bokehApp.py

import holoviews as hv
import numpy as np

import holoviews.operation.datashader as hd
import datashader as ds
from holoviews.operation.datashader import datashade, rasterize, dynspread
from datashader.colors import Sets1to3
import pandas as pd

from bokeh.io import show
from bokeh.layouts import layout, gridplot
from bokeh.models import Slider, Button, AutocompleteInput, Label, Select
from bokeh.plotting import curdoc

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

#get list of named genes - all - full view
def getGenes():
    return db.genesfullv2.distinct('name')

#get expression values for each cell given the gene - full view
def getVals(gene):
    query = db.genesfullv2.find({'name' : gene})
    
    temp = {}
    for doc in query: #for each doc in query, get the value dictionary
        temp = doc['values']

    arr = np.zeros(346264, dtype=int)
    for key in temp:
        arr[int(key)] = 1

    return arr

#get list of named genes
def getGenes_microglia():
    return db.genesfullmicroglia.distinct('name')

#get expression values for each cell given the gene - microglia specific full view
def getVals_microglia(gene):
    query = db.genesfullmicroglia.find({'name' : gene})
    
    temp = {}
    for doc in query: #for each doc in query, get the value dictionary
        temp = doc['values']

    arr = np.zeros(17089, dtype=int)
    for key in temp:
        arr[int(key)] = 1

    return arr

#queried graph view based on catergory of brain cell
def querygraph(gene, set):
	if (set == "microglia"):
		categorical_points = hv.Points((df3["UMAP_1"], df3["UMAP_2"], getVals_microglia(gene)), ['UMAP_1', 'UMAP_2'], vdims='Category')
	else:
		categorical_points = hv.Points((df["UMAP_1"], df["UMAP_2"], getVals(gene)), ['UMAP_1', 'UMAP_2'], vdims='Category')

	return dynspread(datashade(categorical_points, aggregator=ds.count_cat('Category'), color_key=['#c9c9c9', '#00008a'], dynamic=False).opts(plot=dict(width=600, height=450)))

#clustered view based on category of brain cell
def clustersgraph(set):
	if (set == "microglia"):
		categorical_points = hv.Points((df3["UMAP_1"], df3["UMAP_2"], df4["SCT_snn_res.0.2"]), ['UMAP_1', 'UMAP_2'], vdims='Category')
	else:
		categorical_points = hv.Points((df["UMAP_1"], df["UMAP_2"], df2["SCT_snn_res.0.2"]), ['UMAP_1', 'UMAP_2'], vdims='Category')

	return dynspread(datashade(categorical_points, aggregator=ds.count_cat('Category'), color_key=Sets1to3, dynamic=False).opts(plot=dict(width=600, height=450)))


#streams - used for "live updates"
stream = hv.streams.Stream.define('Gene', gene="", set="all")()
streamSet = hv.streams.Stream.define('Set', set="all")()


# graph variables - calls function to get graph objects
dmap_query = hv.DynamicMap(querygraph, streams=[stream])
dmap_cluster = hv.DynamicMap(clustersgraph, streams=[streamSet])



#callbacks intitialized and called here
def modify_doc(doc):

	#callback function
	def autocomplete_update(attrname, old, new):
		stream.event(gene=new)
		print(autocomplete.value)

	#callback function
	def dropdown_update(attrname, old, new):
		streamSet.event(set=new)
		stream.event(set=new)
		print(dropdown.value)

	#initialize dropdown to select cell type
	dropdown = Select(title="Cell Set", value="all",
                   options=['all', 'microglia'])

	#initialize autocomplete field for querying genes
	autocomplete = AutocompleteInput(title="Type in a gene and select from the dropdown", value="", completions=getGenes())

	#callbacks
	dropdown.on_change('value', dropdown_update)
	autocomplete.on_change('value', autocomplete_update)

	#get graphs and store in variables
	hvplot = renderer.get_plot(dmap_query, doc)
	hvplot_full = renderer.get_plot(dmap_cluster, doc)

	#create view for HTML
	plot = gridplot([[autocomplete, dropdown], [hvplot.state, hvplot_full.state]])

	#add view to HTML doc
	doc.add_root(plot)

#call function modify doc to display
doc = modify_doc(curdoc())
