import requests
import datetime
from itertools import repeat
from bokeh.plotting import figure, show
from bokeh.models import HoverTool
from bokeh.layouts import row


def get_data_bitfinex(time_start, time_stop, granularity):
    """

    :param time_start:
    :param time_stop:
    :param granularity:
    :return: raw data: list(milisecond timestamp, O, C, H, L, volume)
    """
    url = f'https://api-pub.bitfinex.com/v2/candles/trade:{granularity}:tBTCUSD/hist'

    payload = {
        'limit': 10000,
        'sort': 1,
        'start': time_start.timestamp() * 1000,
        'end': time_stop.timestamp() * 1000
    }

    r = requests.get(url, params=payload)

    data = r.json()
    print(data)

    return data


def generate_volumes(data, width=50):
    """

    :param data: raw data
    :param width: bin width
    :return: (bins, volumes)
    """
    highest = 0
    lowest = 100000000
    for each in data:
        if each[3] > highest:
            highest = each[3]

        if each[4] < lowest:
            lowest = each[4]

    print('highest price: ', highest)
    print('lowest price:', lowest)

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

    return bins, volumes


def create_candles(data, dark_theme=False):
    y0_green = []
    y1_green = []
    y0_red = []
    y1_red = []
    vbar_green_x = []
    vbar_green_top = []
    vbar_green_bottom = []
    vbar_red_x = []
    vbar_red_top = []
    vbar_red_bottom = []

    for each in data:
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

    bar_width = (data[1][0] - data[0][0]) * 0.7

    candles = figure()
    candles.vbar(vbar_green_x, bar_width, vbar_green_top, vbar_green_bottom, fill_color='green', line_color='green')
    candles.vbar(vbar_red_x, bar_width, vbar_red_top, vbar_red_bottom, fill_color='red', line_color='red')
    candles.segment(vbar_green_x, y0_green, vbar_green_x, y1_green, color='green')
    candles.segment(vbar_red_x, y0_red, vbar_red_x, y1_red, color='red')
    candles.sizing_mode = 'stretch_both'

    if dark_theme:
        candles.border_fill_color = 'dimgray'
        candles.background_fill_color = '#1f1f1f'  # 'dimgray'
        candles.grid.grid_line_color = '#4a4a4a'  # 'black'
        candles.yaxis[0].major_label_text_color = 'white'
        candles.xaxis[0].major_label_text_color = 'white'

        candles.vbar(vbar_green_x, bar_width, vbar_green_top, vbar_green_bottom, fill_color='#75bb36', line_color='#75bb36')
        candles.vbar(vbar_red_x, bar_width, vbar_red_top, vbar_red_bottom, fill_color='#dd4a4a', line_color='#dd4a4a')
        candles.segment(vbar_green_x, y0_green, vbar_green_x, y1_green, color='#75bb36')
        candles.segment(vbar_red_x, y0_red, vbar_red_x, y1_red, color='#dd4a4a')
    else:
        candles.vbar(vbar_green_x, bar_width, vbar_green_top, vbar_green_bottom, fill_color='green', line_color='green')
        candles.vbar(vbar_red_x, bar_width, vbar_red_top, vbar_red_bottom, fill_color='red', line_color='red')
        candles.segment(vbar_green_x, y0_green, vbar_green_x, y1_green, color='green')
        candles.segment(vbar_red_x, y0_red, vbar_red_x, y1_red, color='red')
    return candles


def create_volumes(bins, volumes, height, dark_theme=False):
    plot = figure()
    plot.hbar(y=bins, height=height * 0.7, left=0, right=volumes)
    plot.add_tools(HoverTool())
    plot.sizing_mode = 'stretch_height'

    if dark_theme:
        plot.border_fill_color = 'dimgray'
        plot.background_fill_color = '#1f1f1f'  # 'dimgray'
        plot.grid.grid_line_color = '#4a4a4a'  # 'black'
        plot.yaxis[0].major_label_text_color = 'white'
        plot.xaxis[0].major_label_text_color = 'white'

    return plot


def test():
    time1 = datetime.datetime(2020, 1, 6)
    time2 = datetime.datetime(2020, 4, 26)
    time2 = datetime.datetime.utcnow()
    gr = '3h'

    data = get_data_bitfinex(time1, time2, gr)
    bins, volumes = generate_volumes(data, 10)
    candles = create_candles(data, dark_theme=True)
    volumes = create_volumes(bins, volumes, 10, dark_theme=True)

    layout = row(volumes, candles)
    layout.sizing_mode = 'stretch_both'
    show(layout)
    # show(candles)


if __name__ == '__main__':
    test()
