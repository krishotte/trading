import requests
import datetime
from itertools import repeat
from bokeh.plotting import figure, show
from bokeh.models import HoverTool


time1 = datetime.datetime(2020, 3, 8)
time2 = datetime.datetime(2020, 4, 26, hour=18)
print('tstart: ', time1.timestamp())
print('tend: ', time2.timestamp())

# url = 'https://api-pub.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist'
url = 'https://api-pub.bitfinex.com/v2/candles/trade:1h:tBTCUSD/hist'

payload = {
    'limit': 10000,
    'sort': 1,
    'start': time1.timestamp() * 1000,
    'end': time2.timestamp() * 1000
}

r = requests.get(url, params=payload)

data = r.json()
print(data)

x_green = []
y0_green = []
y1_green = []
x_red = []
y0_red = []
y1_red = []
vbar_green_x = []
vbar_green_top = []
vbar_green_bottom = []
vbar_red_x = []
vbar_red_top = []
vbar_red_bottom = []

for each in data:
    """
    x0.append(each[0])
    x1.append(each[0])
    y0.append(each[4])
    y1.append(each[3])
    """
    if each[1] < each[2]:
        vbar_green_x.append(each[0])
        vbar_green_top.append(each[2])
        vbar_green_bottom.append(each[1])

        y0_green.append(each[4])
        y1_green.append(each[3])
    else:
        vbar_red_x.append(each[0])
        vbar_red_top.append(each[2])
        vbar_red_bottom.append(each[1])

        y0_red.append(each[4])
        y1_red.append(each[3])

"""
plot = figure()
plot.segment(x0, y0, x1, y1)
plot.add_tools(HoverTool())
plot.sizing_mode = 'stretch_both'
"""

candles = figure()
candles.vbar(vbar_green_x, 1000 * 3600, vbar_green_top, vbar_green_bottom, fill_color='green', line_color='green')
candles.vbar(vbar_red_x, 1000 * 3600, vbar_red_top, vbar_red_bottom, fill_color='red', line_color='red')
candles.segment(vbar_green_x, y0_green, vbar_green_x, y1_green, color='green')
candles.segment(vbar_red_x, y0_red, vbar_red_x, y1_red, color='red')
candles.sizing_mode = 'stretch_both'
candles.border_fill_color = 'dimgray'
candles.background_fill_color = 'dimgray'
candles.grid.grid_line_color = 'black'

# show(plot)
# show(candles)
