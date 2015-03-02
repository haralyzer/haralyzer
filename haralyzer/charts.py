import argparse
import json
import pygal
from textwrap import dedent
from haralyzer import HarParser
from urlparse import urlparse


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

    print args

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
        make_load_time_by_content_pie(all_pages)
    elif chart_type == 'load_time_by_content_bar':
        make_load_time_by_content_bar(all_pages)


def make_load_time_by_content_pie(pages):
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


def make_load_time_by_content_bar(pages):
    """
    Renders a bar chart for load time by content type. Unlike the pie chart,
    this shows actual load time in seconds.

    :param page: ``list`` of Instances of HarPage objects.

    :returns: bar chart object
    """
    bar_chart = pygal.Bar()
    bar_chart.x_labels = map(str, pages[0].parser.content_types)
    bar_chart.title = 'Load time by content for {0}'.format(
        'testing')

    for page in pages:
        tld = urlparse(page.url).netloc
        timings = []
        for c_type in page.parser.content_types:
            load_time = getattr(page, '{0}_load_time'.format(c_type))
            timings.append(load_time)

        bar_chart.add(page.url, timings)

    bar_chart.render_to_file('{0}.svg'.format(tld))
