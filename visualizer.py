import requests
import datetime
from itertools import repeat
from bokeh.plotting import figure, show, curdoc, ColumnDataSource
from bokeh.models import HoverTool, Slider, Paragraph, Tabs, Panel, RangeSlider, DateRangeSlider, Range1d, LinearAxis
from bokeh.layouts import row, column
from bokeh.driving import count


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

    url2 = f'https://api-pub.bitfinex.com/v2/candles/trade:{granularity}:tBTCUSD/last'
    # r2 = requests.get(url)
    # print('last data: ', r2.json(), r.json()[-1])

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
        # print('bin_stop: ', bin_stop)

        bin_start = (round(each[4] / width) * width - bin_first) / width
        # print('bin_start :', bin_start)

        for i in range(int(bin_start), int(bin_stop) + 1):
            volumes[i] += each[5] / (bin_stop - bin_start + 1)

        # print('volumes: ', volumes)

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
    def __init__(self, time1, granularity, dark_mode):
        self.time1 = time1  # datetime.datetime(2020, 4, 1)
        self.time2 = datetime.datetime.now()  # utcnow()
        self.granularity = granularity  # '5m'
        self.dark_mode = dark_mode
        if self.dark_mode:
            self.color_green = '#75bb36'
            self.color_red = '#dd4a4a'
            self.color_blue = 'light blue'
            self.color_black = 'white'
            self.color_gray = 'gray'
        else:
            self.color_green = 'green'
            self.color_red = 'red'
            self.color_blue = 'blue'
            self.color_black = 'black'
            self.color_gray = 'gray'

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
        self.red_candles = ColumnDataSource(data={'timestamps': [], 'candles_bottom': [], 'candles_top': []})
        self.blue_volumes = ColumnDataSource(data={'bins': [], 'volumes': []})
        self.actual_line = ColumnDataSource(data={'timestamps': [], 'values': [], 'name': []})
        self.gray_volumes = ColumnDataSource(data={'timestamps': [], 'volumes': []})

        self.create_candles()
        self.select_data('value', self.day_slider.value, self.day_slider.value)
        self.create_candles_plot()
        self.create_volumes_plot()

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
        self.vbar_gray_x = []
        self.vbar_gray = []

        for each in self.raw_data:
            self.vbar_gray_x.append(each[0])
            self.vbar_gray.append(each[5])
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
        """
        initial data select function
        currently not used
        :return:
        """
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
        print('volumes: ', max(self.gray_volumes.data['volumes']))

        y_start = min(
            min(self.green_candles.data['segment_min']),
            min(self.red_candles.data['segment_min'])
        )
        y_end = max(
            max(self.green_candles.data['segment_max']),
            max(self.red_candles.data['segment_max'])
        )
        self.candles.y_range.start = y_start - (y_end - y_start) * 0.15
        self.candles.y_range.end = y_end + (y_end - y_start) * 0.05

        self.candles.extra_y_ranges = {
            'volume_y': Range1d(
                start=0,
                end=max(self.gray_volumes.data['volumes']) * 5,
            ),
            'candles_y': Range1d(
                start=y_start - (y_end - y_start) * 0.15,
                end=y_end + (y_end - y_start) * 0.05,
            )
        }

        self.candles.yaxis.visible = False
        self.candles.add_layout(LinearAxis(y_range_name='candles_y'), 'left')

        self.candles.vbar(
            x='timestamps',
            width=self.time_step * 1000 * 0.7,  # 900000,
            top='volumes',
            bottom=0,
            source=self.gray_volumes,
            fill_color=self.color_gray,
            line_color=self.color_gray,
            fill_alpha=0.4,
            y_range_name='volume_y',
        )
        self.candles.segment(
            x0='timestamps',
            y0='segment_min',
            x1='timestamps',
            y1='segment_max',
            source=self.green_candles,
            color=self.color_green,
            y_range_name='candles_y',
        )
        self.candles.segment(
            x0='timestamps',
            y0='segment_min',
            x1='timestamps',
            y1='segment_max',
            source=self.red_candles,
            color=self.color_red,
            y_range_name='candles_y',
        )
        self.candles.vbar(
            x='timestamps',
            width=self.time_step * 1000 * 0.7,  # 900000,
            top='candles_top',
            bottom='candles_bottom',
            source=self.green_candles,
            fill_color=self.color_green,
            line_color=self.color_green,
            fill_alpha=0.4,
            y_range_name='candles_y',
        )
        self.candles.vbar(
            x='timestamps',
            width=self.time_step * 1000 * 0.7,  # 900000,
            top='candles_top',
            bottom='candles_bottom',
            source=self.red_candles,
            fill_color=self.color_red,
            line_color=self.color_red,
            fill_alpha=0.4,
            y_range_name='candles_y',
        )
        self.candles.line(
            x='timestamps',
            y='values',
            source=self.actual_line,
            line_color=self.color_black,
            line_dash='dashed',
            name='actual_value',
            legend_field='values',
            y_range_name='candles_y',
        )
        hover_tool = HoverTool(
            tooltips=[
                ('time', '@timestamps{%Y-%m-%d %H:%M}'),
                ('open', '@candles_bottom{(0.0)}'),
                ('close', '@candles_top{(0.0)}'),
                ('high', '@segment_max{(0.0)}'),
                ('low', '@segment_min{(0.0)}'),
                ('volume', '@volumes{(0.0)}')
            ],
            formatters={
                '@timestamps': 'datetime'
            },
            # mode='vline'
        )
        self.candles.add_tools(hover_tool)
        # self.candles.output_backend = "webgl"

        print(self.candles.border_fill_color)
        print(self.candles.background_fill_color)
        print(self.candles.yaxis[0].major_label_text_color)

        if self.dark_mode:
            self.candles.border_fill_color = 'dimgray'
            self.candles.background_fill_color = '#060606'  # '#1f1f1f'  # 'dimgray'
            self.candles.grid.grid_line_color = '#4a4a4a'  # 'black'
            self.candles.yaxis[0].major_label_text_color = 'white'
            self.candles.yaxis[1].major_label_text_color = 'white'
            self.candles.xaxis[0].major_label_text_color = 'white'
        else:
            self.candles.border_fill_color = '#ffffff'
            self.candles.background_fill_color = '#ffffff'
            self.candles.grid.grid_line_color = '#e5e5e5'
            self.candles.yaxis[0].major_label_text_color = '#444444'
            self.candles.yaxis[1].major_label_text_color = '#444444'
            self.candles.xaxis[0].major_label_text_color = '#444444'

    def create_volumes_plot(self):
        self.volume_plot = figure()
        self.volume_plot.hbar(
            y='bins',
            height=self.bin_height * 0.7,
            left=0,
            right='volumes',
            source=self.blue_volumes,
            fill_alpha=0.4,
        )
        hover_tool = HoverTool(tooltips=[
            ('price: ', '@bins{(0)}'),
            ('volume: ', '@volumes{(0)}')
        ])
        self.volume_plot.add_tools(hover_tool)
        self.volume_plot.sizing_mode = 'stretch_height'

        if self.dark_mode:
            self.volume_plot.border_fill_color = 'dimgray'
            self.volume_plot.background_fill_color = '#060606'  # 'dimgray'
            self.volume_plot.grid.grid_line_color = '#4a4a4a'  # 'black'
            self.volume_plot.yaxis[0].major_label_text_color = 'white'
            self.volume_plot.xaxis[0].major_label_text_color = 'white'
        else:
            self.volume_plot.border_fill_color = '#ffffff'
            self.volume_plot.background_fill_color = '#ffffff'
            self.volume_plot.grid.grid_line_color = '#e5e5e5'
            self.volume_plot.yaxis[0].major_label_text_color = '#444444'
            self.volume_plot.xaxis[0].major_label_text_color = '#444444'

    def select_data(self, attr, old, new):
        """
        day_slider value change callback function
        :param attr:
        :param old:
        :param new:
        :return:
        """
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
            'timestamps': self.vbar_green_x[i:j+1],
            'candles_bottom': self.vbar_green_bottom[i:j+1],
            'candles_top': self.vbar_green_top[i:j+1],
            'segment_min': self.segment_y0_green[i:j+1],
            'segment_max': self.segment_y1_green[i:j+1],
        }

        for k in range(len(self.vbar_red_x)):
            if self.vbar_red_x[k] >= start_timestamp:
                break

        # if self.day_slider.value < self.day_slider.end:
        for l in range(len(self.vbar_red_x)):
            if self.vbar_red_x[l] >= stop_timestamp:
                break

        self.red_candles.data = {
            'timestamps': self.vbar_red_x[k:l+1],
            'candles_bottom': self.vbar_red_bottom[k:l+1],
            'candles_top': self.vbar_red_top[k:l+1],
            'segment_min': self.segment_y0_red[k:l+1],
            'segment_max': self.segment_y1_red[k:l+1],
        }

        raw_data_start = int(self.day_slider.value * self.day_length)
        raw_data_stop = int(raw_data_start + self.day_length)

        self.gray_volumes.data = {
            'timestamps': self.vbar_gray_x[raw_data_start:raw_data_stop],
            'volumes': self.vbar_gray[raw_data_start:raw_data_stop],
        }

        self.bin_height = 5
        bins, volumes = generate_volumes(self.raw_data[raw_data_start:raw_data_stop], self.bin_height)
        self.bins = bins
        self.volumes = volumes
        self.blue_volumes.data = {
            'bins': self.bins,
            'volumes': self.volumes,
        }
        self.update_ranges()

    def update_last_value(self):
        url2 = f'https://api-pub.bitfinex.com/v2/candles/trade:{self.granularity}:tBTCUSD/last'
        r2 = requests.get(url2)
        print('last data: ', datetime.datetime.fromtimestamp(r2.json()[0]/1000), r2.json())

        # x = [self.raw_data[0][0], self.raw_data[-1][0]]
        x = [
            min(self.green_candles.data['timestamps'][0], self.red_candles.data['timestamps'][0]),
            max(self.green_candles.data['timestamps'][-1], self.red_candles.data['timestamps'][-1])
        ]
        y = [round(r2.json()[2], 1), round(r2.json()[2], 1)]
        # self.actual_line.data = {'timestamps': x, 'values': y, 'name': [str(y[0]), str(y[-1])]}
        self.actual_line.data = {'timestamps': x, 'values': y}  # , 'name': str(y[0])}

    def update_everything(self):
        self.raw_data = get_data_bitfinex(self.time1, datetime.datetime.now(), self.granularity)
        self.create_candles()
        # self.select_data_()
        self.select_data('value', self.day_slider.value, self.day_slider.value)

    def update_ranges(self):
        try:
            print('updating ranges')
            y_start = min(
                min(self.green_candles.data['segment_min']),
                min(self.red_candles.data['segment_min'])
            )
            y_end = max(
                max(self.green_candles.data['segment_max']),
                max(self.red_candles.data['segment_max'])
            )
            self.candles.y_range.start = y_start - (y_end - y_start) * 0.15
            self.candles.y_range.end = y_end + (y_end - y_start) * 0.05
            self.candles.extra_y_ranges['candles_y'].start = y_start - (y_end - y_start) * 0.15
            self.candles.extra_y_ranges['candles_y'].end = y_end + (y_end - y_start) * 0.05

            print('min: ', y_start, self.candles.y_range.start)
            print('max: ', y_end, self.candles.y_range.end)

            self.candles.extra_y_ranges['volume_y'].end = max(self.gray_volumes.data['volumes']) * 5
        except AttributeError:
            print('ranges not updated')


class VariableDocument(Document):
    def __init__(self, time1, granularity, dark_mode):
        self.time1 = time1  # datetime.datetime(2020, 4, 1)
        self.time2 = datetime.datetime.now()  # utcnow()
        self.granularity = granularity  # '5m'
        self.dark_mode = dark_mode
        if self.dark_mode:
            self.color_green = '#75bb36'
            self.color_red = '#dd4a4a'
            self.color_blue = 'light blue'
            self.color_black = 'white'
            self.color_gray = 'gray'
        else:
            self.color_green = 'green'
            self.color_red = 'red'
            self.color_blue = 'blue'
            self.color_black = 'black'
            self.color_gray = 'gray'

        self.raw_data = get_data_bitfinex(self.time1, self.time2, self.granularity)
        start = self.raw_data[0][0]
        dt_start = datetime.datetime.fromtimestamp(start / 1000)
        end = self.raw_data[-1][0]
        dt_end = datetime.datetime.fromtimestamp(end / 1000)
        print('start ts: ', start, dt_start)
        print('end ts: ', end, dt_end)

        self.range_slider = RangeSlider(start=start, end=end, value=(start, end), step=3600000, title='Selected period')
        self.range_slider2 = DateRangeSlider(start=dt_start, end=dt_end, value=(dt_start, dt_end), step=1)
        self.range_slider.on_change('value', self.update_paragraph)
        self.range_slider.on_change('value_throttled', self.select_data)

        self.range_slider_value = str(dt_start) + ' : ' + str(dt_end)
        self.paragraph = Paragraph(text='')

        self.time_step = (self.raw_data[1][0] - self.raw_data[0][0]) / 1000
        print('delta (s): ', self.time_step)

        self.green_candles = ColumnDataSource(data={'timestamps': [], 'candles_bottom': [], 'candles_top': []})
        self.red_candles = ColumnDataSource(data={'timestamps': [], 'candles_bottom': [], 'candles_top': []})
        self.blue_volumes = ColumnDataSource(data={'bins': [], 'volumes': []})
        self.actual_line = ColumnDataSource(data={'timestamps': [], 'values': []})
        self.gray_volumes = ColumnDataSource(data={'timestamps': [], 'volumes': []})

        self.create_candles()
        self.update_paragraph('text', '', '')
        self.select_data('value', self.range_slider.value, self.range_slider.value)
        self.create_candles_plot()
        self.create_volumes_plot()

    def update_paragraph(self, attr, old, new):
        value1 = datetime.datetime.fromtimestamp(self.range_slider.value[0] / 1000)
        value2 = datetime.datetime.fromtimestamp(self.range_slider.value[1] / 1000)
        self.paragraph.text = str(value1) + ' : ' + str(value2)
        # self.select_data('value', self.range_slider.value, self.range_slider.value)

    def select_data(self, attr, old, new):
        start = self.range_slider.start
        end = self.range_slider.end
        value1 = self.range_slider.value[0]
        value2 = self.range_slider.value[1]
        index1 = (value1 - start) / (self.time_step * 1000)
        index2 = (value2 - start) / (self.time_step * 1000) + 1

        print('indexes: ', index1, ', ', index2)

        # start_timestamp = self.raw_data[int(self.day_slider.value * self.day_length)][0]
        # stop_timestamp = self.raw_data[int((self.day_slider.value + 1) * self.day_length)][0]

        # i = int(index1)
        # j = int(index2)

        for i in range(len(self.vbar_green_x)):
            if self.vbar_green_x[i] >= value1:
                break

        for j in range(len(self.vbar_green_x)):
            if self.vbar_green_x[j] >= value2:
                break

        self.green_candles.data = {
            'timestamps': self.vbar_green_x[i:j+1],
            'candles_bottom': self.vbar_green_bottom[i:j+1],
            'candles_top': self.vbar_green_top[i:j+1],
            'segment_min': self.segment_y0_green[i:j+1],
            'segment_max': self.segment_y1_green[i:j+1],
        }

        for k in range(len(self.vbar_red_x)):
            if self.vbar_red_x[k] >= value1:
                break

        # if self.day_slider.value < self.day_slider.end:
        for l in range(len(self.vbar_red_x)):
            if self.vbar_red_x[l] >= value2:
                break

        self.red_candles.data = {
            'timestamps': self.vbar_red_x[k:l+1],
            'candles_bottom': self.vbar_red_bottom[k:l+1],
            'candles_top': self.vbar_red_top[k:l+1],
            'segment_min': self.segment_y0_red[k:l+1],
            'segment_max': self.segment_y1_red[k:l+1],
        }

        raw_data_start = int(index1)  # int(self.day_slider.value * self.day_length)
        raw_data_stop = int(index2)  # int(raw_data_start + self.day_length)

        self.gray_volumes.data = {
            'timestamps': self.vbar_gray_x[raw_data_start:raw_data_stop],
            'volumes': self.vbar_gray[raw_data_start:raw_data_stop],
        }

        self.bin_height = 50
        bins, volumes = generate_volumes(self.raw_data[raw_data_start:raw_data_stop], self.bin_height)
        self.bins = bins
        self.volumes = volumes
        self.blue_volumes.data = {
            'bins': self.bins,
            'volumes': self.volumes,
        }

# if __name__ == '__main__':
#    test()


time1 = datetime.datetime(2020, 4, 25)
granularity = '5m'

doc = Document(time1, granularity, dark_mode=True)
doc.candles.sizing_mode = 'stretch_both'
# doc.sizing_mode = 'stretch_both'
doc.volume_plot.y_range = doc.candles.extra_y_ranges['candles_y']

row1 = row(doc.volume_plot, doc.candles)
row1.sizing_mode = 'stretch_both'

layout = column(doc.day_slider, row1)
layout.sizing_mode = 'stretch_both'

tab1 = Panel(child=layout, title='daily')


time2 = datetime.datetime(2019, 1, 1)
vardoc = VariableDocument(time2, '1D', dark_mode=True)
vardoc.candles.sizing_mode = 'stretch_both'
vardoc.volume_plot.y_range = vardoc.candles.y_range

row2 = row(vardoc.volume_plot, vardoc.candles)
row2.sizing_mode = 'stretch_both'

vardoc_layout = column(vardoc.range_slider, vardoc.paragraph, row2)
vardoc_layout.sizing_mode = 'stretch_both'

tab2 = Panel(child=vardoc_layout, title='variable')
tabs = Tabs(tabs=[tab1, tab2])
curdoc().add_root(tabs)
curdoc().add_periodic_callback(doc.update_last_value, 2000)
curdoc().add_periodic_callback(doc.update_everything, 60000)

# start bokeh server by 'bokeh serve --show visualizer.py'
