=========
Haralyzer
=========

.. image:: https://badge.fury.io/py/haralyzer.svg
    :target: http://badge.fury.io/py/haralyzer

.. image:: https://travis-ci.org/mrname/haralyzer.svg?branch=master
    :target: https://travis-ci.org/mrname/haralyzer

.. image:: https://coveralls.io/repos/mrname/haralyzer/badge.svg?branch=master
  :target: https://coveralls.io/r/mrname/haralyzer?branch=master

.. image:: https://readthedocs.org/projects/haralyzer/badge/?version=latest
    :target: http://haralyzer.readthedocs.org/en/latest/

A Python Framework For Using HAR Files To Analyze Web Pages.

Overview
--------

The haralyzer module contains two classes for analyzing web pages based
on a HAR file. ``HarParser()`` represents a full file (which might have
multiple pages), and ``HarPage()`` represents a single page from said file.

``HarParser`` has a couple of helpful methods for analyzing single entries
from a HAR file, but most of the pertinent functions are inside of the page
object.

``haralyzer`` was designed to be easy to use, but you can also access more
powerful functions directly.

Quick Intro
-----------

HarParser
+++++++++

The ``HarParser`` takes a single argument of a ``dict`` representing the JSON
of a full HAR file. It has the same properties of the HAR file, EXCEPT that each
page in HarParser.pages is a HarPage object::

    import json
    from haralyzer import HarParser, HarPage

    with open('har_data.har', 'r') as f:
        har_parser = HarParser(json.loads(f.read()))

    print har_parser.browser
    # {u'name': u'Firefox', u'version': u'25.0.1'}

    for page in har_parser.pages:
        assert isinstance(page, HarPage, None)
        # returns True for each

HarPage
+++++++

The ``HarPage`` object contains most of the goods you need to easily analyze a
page. It has helper methods that are accessible, but most of the data you need is
in properties for easy access. You can create a HarPage object directly by giving
it the page ID (yes, I know it is stupid, it's just how HAR is organized), and either
a ``HarParser`` with `har_parser=parser`, or a ``dict`` representing the JSON of a full HAR
file (see example above) with `har_data=har_data`::

    import json
    From haralyzer import HarPage

    with open('har_data.har', 'r') as f:
        har_page = HarPage('page_3', har_data=json.loads(f.read()))

    ### WORK WITH LOAD TIMES (all load times are in ms) ###

    # Get image load time in milliseconds as rendered by the browser
    har_page.image_load_time
    # prints 713

    # We could do this with 'css', 'js', 'html', 'audio', or 'video'

    ### WORK WITH SIZES (all sizes are in bytes) ###

    # Get the total page size (with all assets)
    har_page.page_size
    # prints 2423765

    # Get the total image size
    har_page.image_size
    # prints 733488
    # We could do this with 'css', 'js', 'html', 'audio', or 'video'


MultiHarParser
++++++++++++++

The ``MutliHarParser`` takes a ``list`` of ``dict``, each of which represents the JSON
of a full HAR file. The concept here is that you can provide multiple HAR files of the
same page (representing multiple test runs) and the ``MultiHarParser`` will provide
aggregate results for load times::

    import json
    from haralyzer import HarParser, HarPage

    test_runs = []
    with open('har_data1.har', 'r') as f1:
        test_runs.append( (json.loads( f1.read() ) )
    with open('har_data2.har', 'r') as f2:
        test_runs.append( (json.loads( f2.read() ) )

    multi_har_parser = MultiHarParser(har_data=test_runs)

    # Get the mean for the time to first byte of all runs in MS
    print multi_har_parser.time_to_first_byte
    # 70

    # Get the total page load time mean for all runs in MS
    print multi_har_parser.load_time
    # 150

    # Get the javascript load time mean for all runs in MS
    print multi_har_parser.js_load_time
    # 50

    # You can get the standard deviation for any of these as well
    # Let's get the standard deviation for javascript load time
    print multi_har_parser.get_stdev('js')
    # 5
    # We can also do that with 'page' or 'ttfb' (time to first byte)
    print multi_har_parser.get_stdev('page')
    # 11
    print multi_har_parser.get_stdev('ttfb')
    # 10

    ### DECIMAL PRECISION ###

    # You will notice that all of the results are above. That is because
    # the default decimal precision for the multi parser is 0. However, you
    # can pass whatever you want into the constructor to control this.

    multi_har_parser = MultiHarParser(har_data=test_runs, decimal_precision=2)
    print multi_har_parser.time_to_first_byte
    # 70.15


Advanced Usage
==============

``HarPage`` includes a lot of helpful properties, but they are all
easily produced using the public methods of ``HarParser`` and ``HarPage``::

    import json
    from haralyzer import HarPage

    with open('har_data.har', 'r') as f:
        har_page = HarPage('page_3', har_data=json.loads(f.read()))

    ### ACCESSING FILES ###

    # You can get a JSON representation of all assets using HarPage.entries #
    for entry in har_page.entries:
        if entry['startedDateTime'] == 'whatever I expect':
            ... do stuff ...

    # It also has methods for filtering assets #
    # Get a collection of entries that were images in the 2XX status code range #
    entries = har_page.filter_entries(content_type='image.*', status_code='2.*')

    # Get the size of the collection we just made #
    collection_size = har_page.get_total_size(entries)

    # We can also access files by type with a property #
    for js_file in har_page.js_files:
        ... do stuff ....

    ### GETTING LOAD TIMES ###

    # Get the BROWSER load time for all images in the 2XX status code range #
    load_time = har_page.get_load_time(content_type='image.*', status_code='2.*')

    # Get the TOTAL load time for all images in the 2XX status code range #
    load_time = har_page.get_load_time(content_type='image.*', status_code='2.*', async=False)

This could potentially be out of date, so please check out the sphinx docs.


More.... Advanced Usage
=======================

All of the HarPage methods above leverage stuff from the HarParser,
some of which can be useful for more complex operations. They either
operate on a single entry (from a HarPage) or a ``list`` of entries::

    import json
    from haralyzer import HarParser

    with open('har_data.har', 'r') as f:
        har_parser = HarParser(json.loads(f.read()))

    for page in har_parser.pages:
        for entry in page.entries:
            ### MATCH HEADERS ###
            if har_parser.match_headers(entry, 'Content-Type', 'image.*'):
                print 'This would appear to be an image'
            ### MATCH REQUEST TYPE ###
            if har_parser.match_request_type(entry, 'GET'):
                print 'This is a GET request'
            ### MATCH STATUS CODE ###
            if har_parser.match_status_code(entry, '2.*'):
                print 'Looks like all is well in the world'


Asset Timelines
+++++++++++++++

The last helper function of ``HarParser`` requires it's own section, because it
is odd, but can be helpful, especially for creating charts and reports.

It can create an asset timeline, which gives you back a ``dict`` where each
key is a ``datetime`` object, and the value is a ``list`` of assets that were
loading at that time. Each value of the ``list`` is a ``dict`` representing
an entry from a page.

It takes a ``list`` of entries to analyze, so it assumes that you have
already filtered the entries you want to know about::

    import json
    from haralyzer import HarParser

    with open('har_data.har', 'r') as f:
        har_parser = HarParser(json.loads(f.read()))

    ### CREATE A TIMELINE OF ALL THE ENTRIES ###
    entries = []
    for page in har_parser.pages:
        for entry in page.entries:
            entries.append(entry)

    timeline = har_parser.create_asset_timeline(entries)

    for key, value in timeline.items():
        print(type(key))
        # <type 'datetime.datetime'>
        print(key)
        # 2015-02-21 19:15:41.450000-08:00
        print(type(value))
        # <type 'list'>
        print(value)
        # Each entry in the list is an asset from the page
        # [{u'serverIPAddress': u'157.166.249.67', u'cache': {}, u'startedDateTime': u'2015-02-21T19:15:40.351-08:00', u'pageref': u'page_3', u'request': {u'cookies':............................


With this, you can examine the timeline for any number of assets. Since the key is a ``datetime``
object, this is a heavy operation. We could always change this in the future, but for now,
limit the assets you give this method to only what you need to examine.
