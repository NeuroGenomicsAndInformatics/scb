# bokehApp.py

import holoviews as hv
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
import numpy as np

import holoviews.operation.datashader as hd
import datashader as ds
from holoviews.operation.datashader import datashade, dynspread
from datashader.colors import Sets1to3
import pandas as pd


df = pd.read_csv('../textfiles/umap.txt', delimiter=' ')
df2 = pd.read_csv('../textfiles/metadata.txt', delimiter=' ')

hv.extension('bokeh', 'matplotlib')
renderer = hv.renderer('bokeh')
renderer = renderer.instance(mode='server')


if __name__ == '__main__':

    categorical_points = hv.Points((df["UMAP_1"], df["UMAP_2"], df2["SCT_snn_res.0.2"]), ['UMAP_1', 'UMAP_2'], vdims='Category')

    dmap = dynspread(datashade(categorical_points, aggregator=ds.count_cat('Category'), color_key=Sets1to3).opts(plot=dict(width=600, height=450)))

    app = renderer.app(dmap)
    server = Server({'/': app}, port=port, allow_websocket_origin=[link]) #####################
    server.start()
    loop = IOLoop.current()
    loop.start()