Asset Timeline
===============
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