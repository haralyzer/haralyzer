import argparse
import json
import pygal
from textwrap import dedent
from haralyzer import HarParser
from urlparse import urlparse
import time
import pdb


def har_chart_cli():
    """
    CLI Tool for creating charts from HAR files.
    """
    usage_str = 'Create charts'
    parser = argparse.ArgumentParser(description="Create charts from HAR "
                                     "files using pygal",
                                     usage=dedent(usage_str))
    parser.add_argument('chart_type', type=str, help="type of chart to create")
    parser.add_argument('har_files', type=str, nargs='+',
                        help="files to use for the chart")

    args = parser.parse_args()

    make_chart(chart_type=args.chart_type, har_files=args.har_files)


def make_chart(chart_type=None, har_files=None):
    """
    Makes a chart
    """
    if chart_type is None or har_files is None:
        raise ValueError('A chart_type and at least one HAR file is required')

    all_pages = []
    for har_file in har_files:
        with open(har_file, 'r') as f:
            har_parser = HarParser(json.loads(f.read()))
            all_pages.extend(har_parser.pages)

    if chart_type == 'load_time_by_content_pie':
        load_time_by_content_pie(all_pages)
    elif chart_type == 'load_time_by_content_bar':
        load_time_by_content_bar(all_pages)
    elif chart_type == 'load_time_by_content_stacked_bar':
        load_time_by_content_stacked_bar(all_pages)
    elif chart_type == 'total_load_time':
        total_load_time(all_pages)
    elif chart_type == 'size_by_content':
        size_by_content_pie(all_pages)


def load_time_by_content_pie(pages):
    """
    Renders a pie chart for load time by content type, showing the percentage
    of the load time of each asset type in relation to the total load time.
    One chart will be created for each page in the ``pages`` argument.

    :param pages: ``list`` of Instances of a HarPage object
    """
    for page in pages:
        tld = urlparse(page.url).netloc
        total_load_time = page.total_load_time
        pie_chart = pygal.Pie()
        pie_chart.title = 'Load time by content for {0}'.format(
            page.url)
        rows = []
        for c_type in page.parser.content_types:
            load_time = getattr(page, '{0}_load_time'.format(c_type))
            percent = 100 * float(load_time)/float(total_load_time)
            rows.append((c_type, percent))

        # Sort the rows by highest percentage
        rows = sorted(rows, key=lambda row: row[1], reverse=True)
        for row in rows:
            pie_chart.add('{0} {1:.0f}%'.format(row[0], row[1]), row[1])

        pie_chart.render_to_file('{0}.svg'.format(tld))


def load_time_by_content_bar(pages):
    """
    Renders a bar chart for load time by content type. Unlike the pie chart,
    this shows actual load time in seconds.

    :param page: ``list`` of Instances of HarPage objects.

    :returns: bar chart object
    """
    bar_chart = pygal.Bar()
    bar_chart.x_labels = map(str, pages[0].parser.content_types)
    bar_chart.title = 'Load time by content for {0}'.format(
        '"testing" in seconds')

    timings = dict()
    all_times = []
    for page in pages:
        tld = urlparse(page.url).netloc
        # This will end up being a big ``list`` of dict. Each key is the name
        # of the page, and the value is a ``list`` of the content type timings
        page_timings = []
        for c_type in page.parser.content_types:
            page_timings.append(getattr(page, '{0}_load_time'.format(c_type)))

        # timings.append({'name': page.url, 'timings': page_timings})
        timings[tld] = page_timings
        all_times.extend(page_timings)

        # Get multiplier for all values
        for page_id, timeset in timings.iteritems():
            all_times.extend(timeset)

    scale, multiplier = _create_multiplier(all_times, val_type='time')

    bar_chart.title = 'Load time by content in {0}'.format(scale)

    for page_id, timeset in timings.iteritems():
        bar_chart.add(page_id, [t * multiplier for t in timeset])

    bar_chart.render_to_file('{0}.svg'.format(tld))


def load_time_by_content_stacked_bar(pages):
    """
    Renders a bar chart for load time by content type. Unlike the pie chart,
    this shows actual load time in seconds.

    :param pages: ``list`` of Instances of HarPage objects.

    :returns: bar chart object
    """
    bar_chart = pygal.StackedBar()
    page_titles = []
    for page in pages:
        page_titles.append(page.url)
    bar_chart.x_labels = map(str, page_titles)
    bar_chart.title = 'Load time by content for {0}'.format(
        '"testing" in seconds')

    # timings needs to be a dict where the key is the content type, and the
    # value is a list of the load times for each content type. The way that
    # pygal works, the order of the value list represents the load time of that
    # element on the X axis
    # http://pygal.org/chart_types/#idid2
    timings = dict()

    # We need to remove the misc files from this because we do not care!
    content_types = page.parser.content_types
    content_types.remove('misc')

    for c_type in content_types:
        timings[c_type] = []

    page_timings = []
    for page in pages:
        page_time = 0
        for c_type in content_types:
            load_time = getattr(page, '{0}_load_time'.format(c_type))
            page_time += load_time
            timings[c_type].append(load_time)
        page_timings.append(page_time)

    # Add the arrays for each content type
    for c_type, vals in timings.iteritems():
        bar_chart.add(c_type, vals)

    pdb.set_trace()
    # Add the total load time for each page. Since we want the full bar to
    # represent the total load time, we actually need to give it the value of
    # (total_load_time - all_load_times_added_thus_far)
    total_load_times = []
    for i in range(len(pages)):
        total_load_times.append(pages[i].total_load_time - page_timings[i])
    bar_chart.add('Total', total_load_times)

    bar_chart.render_to_file('{0}.svg'.format(time.time()))


def total_load_time(pages):
    """
    Renders a bar chart of the total load time for each page.
    """
    bar_chart = pygal.Bar()
    all_load_times = []
    load_times = dict()
    for page in pages:
        all_load_times.append(page.total_load_time)
        tld = urlparse(page.url).netloc
        load_times[tld] = page.total_load_time

    scale, multiplier = _create_multiplier(all_load_times, val_type='time')

    bar_chart.title = 'Load time by content in {0}'.format(scale)

    for page_id, timing in load_times.iteritems():
        bar_chart.add(page_id, [timing * multiplier])

    bar_chart.render_to_file('{0}.svg'.format(tld))


def size_by_content_pie(pages):
    """
    Renders a pie chart for load time by content type, showing the percentage
    of the load time of each asset type in relation to the total load time.
    One chart will be created for each page in the ``pages`` argument.

    :param pages: ``list`` of Instances of a HarPage object
    """
    for page in pages:
        tld = urlparse(page.url).netloc
        total_size = page.total_page_size
        pie_chart = pygal.Pie()
        pie_chart.title = 'Page size by content for {0}'.format(
            page.url)
        rows = []
        for c_type in page.parser.content_types:
            content_size = getattr(page, 'total_{0}_size'.format(c_type))
            percent = 100 * float(content_size)/float(total_size)
            rows.append((c_type, percent))

        # Sort the rows by highest percentage
        rows = sorted(rows, key=lambda row: row[1], reverse=True)
        for row in rows:
            pie_chart.add('{0} {1:.0f}%'.format(row[0], row[1]), row[1])

        pie_chart.render_to_file('{0}.svg'.format(tld))


def timeline(pages):
    """
    Renders a basic timeline of the given assets
    """
    pass


def _render_bar_chart():
    """
    Renders a bar chart
    """
    pass


def _render_pie_chart():
    """
    Renders a pie chart
    """
    pass


def _create_multiplier(vals, val_type=''):
    """
    Takes an array of values and returns the proper multiplier for
    scaling charts.

    :param vals: a ``list`` of ``int`` of the vals to examine
    :param val_type: ``str`` of value type, valid values are:

        * time - this assumes that all input is in ms
        * size = this assumes that all input is in bytes

    :returns: ``typle`` where [0] is a ``str`` of unit type, and [1] is
    an``int`` of the multiplier to scale by
    """
    if val_type == 'time':
        # If something is less than two seconds... keep it at ms
        if any(v <= 2000 for v in vals):
            return ('ms', 1)
        # For now, we will only scale to seconds at the greatest
        else:
            return ('seconds', 1000)
    elif val_type == 'size':
        # If something is less than 1 MB, scale to KB
        if any(v <= 1000000 for v in vals):
            return ('KB', 1024)
        # As of right now, we only scale up to MB
        else:
            return ('MB', 2048)
