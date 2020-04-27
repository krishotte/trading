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

highest = 0
lowest = 100000
for each in data:
    time_ = datetime.datetime.fromtimestamp(each[0]/1000)
    print(time_)

    if each[3] > highest:
        highest = each[3]

    if each[4] < lowest:
        lowest = each[4]

print('highest: ', highest)
print('lowest:', lowest)

width = 10
bin_first = (lowest // width) * width
bin_last = (highest // width + 1) * width

bins = list(range(int(bin_first), int(bin_last + width), int(width)))
volumes = list(repeat(0, len(bins)))

for each in data:
    bin_stop = (bin_last - round(each[3] / width) * width) / width
    bin_stop = len(bins) - bin_stop - 1
    print('bin_stop: ', bin_stop)

    bin_start = (round(each[4] / width) * width - bin_first) / width
    print('bin_start :', bin_start)

    for i in range(int(bin_start), int(bin_stop) + 1):
        volumes[i] += each[5] / (bin_stop - bin_start + 1)

    print('volumes: ', volumes)

# bokeh visualiztion of volumes histogram
plot = figure()
plot.hbar(y=bins, height=7, left=0, right=volumes)
plot.add_tools(HoverTool())
plot.sizing_mode = 'stretch_height'

# show(plot)
