import candles
import volume

from bokeh.plotting import show
from bokeh.layouts import row

layout = row(volume.plot, candles.candles)
layout.sizing_mode = 'stretch_both'
# layout.background = 'black'
show(layout)