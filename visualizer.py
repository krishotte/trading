import requests
import datetime
from itertools import repeat
from bokeh.plotting import figure, show, curdoc, ColumnDataSource
from bokeh.models import HoverTool, Slider, Paragraph
from bokeh.layouts import row, column


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
    # print(data)

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

    candles = figure(x_axis_type='datetime')
    candles.vbar(vbar_green_x, bar_width, vbar_green_top, vbar_green_bottom, fill_color='green', line_color='green')
    candles.vbar(vbar_red_x, bar_width, vbar_red_top, vbar_red_bottom, fill_color='red', line_color='red')
    candles.segment(vbar_green_x, y0_green, vbar_green_x, y1_green, color='green')
    candles.segment(vbar_red_x, y0_red, vbar_red_x, y1_red, color='red')
    candles.sizing_mode = 'stretch_both'
    # candles.x_axis_type = 'datetime'

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
    # time1 = datetime.datetime(2020, 1, 6)
    # time1 = datetime.datetime(2019, 1, 4)
    time1 = datetime.datetime(2020, 5, 1)
    time2 = datetime.datetime(2020, 5, 1)
    time2 = datetime.datetime.utcnow()
    gr = '15m'

    days = time2 - time1
    print('days', days.days)

    day_slider = Slider(start=0, end=1 + days.days, value=1 + days.days, step=1, title='Day Selector')
    day_slider.on_change('value', update_source_data)

    data = get_data_bitfinex(time1, time2, gr)
    bins, volumes = generate_volumes(data, 10)
    candles = create_candles(data, dark_theme=True)
    volumes = create_volumes(bins, volumes, 10, dark_theme=True)

    layout = row(volumes, candles)
    layout.sizing_mode = 'stretch_both'

    document = column(day_slider, layout)
    document.sizing_mode = 'stretch_both'

    # show(document)
    # show(layout)
    # show(candles)
    curdoc().add_root(document)


def update_source_data(attr, old, new):
    print('slider value changed')


class Document:
    def __init__(self, time1, granularity):
        self.time1 = time1  # datetime.datetime(2020, 4, 1)
        self.time2 = datetime.datetime.utcnow()
        self.granularity = granularity  # '5m'

        self.days = self.time2 - self.time1
        print('days', self.days.days)

        self.day_slider = Slider(start=0, end=self.days.days, value=self.days.days, step=1, title='Day Selector')
        self.day_slider.on_change('value', self.select_data)

        self.raw_data = get_data_bitfinex(self.time1, self.time2, self.granularity)
        self.time_step = (self.raw_data[1][0] - self.raw_data[0][0]) / 1000
        self.day_length = 86400 / self.time_step

        print('delta (s): ', self.time_step)
        print('day length: ', self.day_length)
        print('raw data length: ', len(self.raw_data))
        print('actual data start: ', self.day_slider.value * self.day_length)

        self.green_candles = ColumnDataSource(data={'timestamps': [], 'candles_bottom': [], 'candles_top': []})
        # self.red_candles = ColumnDataSource(data=None)
        # self.blue_volumes = ColumnDataSource(data=None)

        self.create_candles()
        self.select_data_()
        self.create_candles_plot()
        # bins, volumes = generate_volumes(self.raw_data, 10)
        # self.bins = bins
        # self.volumes = volumes
        # candles_plot = create_candles(data, dark_theme=True)
        # volumes_plot = create_volumes(bins, volumes, 10, dark_theme=True)

    def create_candles(self):
        self.segment_y0_green = []
        self.segment_y1_green = []
        self.segment_y0_red = []
        self.segment_y1_red = []
        self.vbar_green_x = []
        self.vbar_green_top = []
        self.vbar_green_bottom = []
        self.vbar_red_x = []
        self.vbar_red_top = []
        self.vbar_red_bottom = []

        for each in self.raw_data:
            if each[1] < each[2]:
                self.vbar_green_x.append(each[0])
                self.vbar_green_top.append(each[2])
                self.vbar_green_bottom.append(each[1])

                self.segment_y0_green.append(each[4])
                self.segment_y1_green.append(each[3])
            else:
                self.vbar_red_x.append(each[0])
                self.vbar_red_top.append(each[2])
                self.vbar_red_bottom.append(each[1])

                self.segment_y0_red.append(each[4])
                self.segment_y1_red.append(each[3])

    def select_data_(self):
        start_timestamp = self.raw_data[int(self.day_slider.value * self.day_length)][0]
        print('searchin for timestamp ', start_timestamp)

        for i in range(len(self.vbar_green_x)):
            if self.vbar_green_x[i] >= start_timestamp:
                break
        print('timestamp found ', self.vbar_green_x[i])

        self.green_candles.data = {
            'timestamps': self.vbar_green_x[i:-1],
            'candles_bottom': self.vbar_green_bottom[i:-1],
            'candles_top': self.vbar_green_top[i:-1]
        }

    def create_candles_plot(self):
        self.candles = figure(x_axis_type='datetime')
        self.candles.vbar(
            x='timestamps',
            width=900000,
            top='candles_top',
            bottom='candles_bottom',
            source=self.green_candles,
            fill_color='green',
            line_color='green'
        )

    def select_data(self, attr, old, new):
        print('slider value changed: ', new)

        start_timestamp = self.raw_data[int(self.day_slider.value * self.day_length)][0]
        try:
            stop_timestamp = self.raw_data[int((self.day_slider.value + 1) * self.day_length)][0]
        except IndexError:
            stop_timestamp = self.raw_data[-1][0]

        for i in range(len(self.vbar_green_x)):
            if self.vbar_green_x[i] >= start_timestamp:
                break

        # if self.day_slider.value < self.day_slider.end:
        for j in range(len(self.vbar_green_x)):
            if self.vbar_green_x[j] >= stop_timestamp:
                break

        self.green_candles.data = {
            'timestamps': self.vbar_green_x[i:j],
            'candles_bottom': self.vbar_green_bottom[i:j],
            'candles_top': self.vbar_green_top[i:j]
        }


# if __name__ == '__main__':
#    test()
# test()

time1 = datetime.datetime(2020, 4, 25)
granularity = '15m'

doc = Document(time1, granularity)
doc.candles.sizing_mode = 'stretch_both'

layout = column(doc.day_slider, doc.candles)
layout.sizing_mode = 'stretch_both'
curdoc().add_root(layout)

# start bokeh server by 'bokeh serve --show visualizer.py'
