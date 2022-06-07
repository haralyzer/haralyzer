HarParser
+++++++++

The ``HarParser`` takes a single argument of a ``dict`` representing the JSON
of a full HAR file. It has the same properties of the HAR file, EXCEPT that each
page in HarParser.pages is a HarPage object. ::

    import json
    from haralyzer import HarParser, HarPage

    with open('har_data.har', 'r') as f:
        har_parser = HarParser(json.loads(f.read()))

    print har_parser.browser
    # {u'name': u'Firefox', u'version': u'25.0.1'}

    print har_parser.hostname
    # 'humanssuck.net'

    for page in har_parser.pages:
        assert isinstance(page, HarPage, None)
        # returns True for each


You can also use either ``from_file()`` or ``from_string()`` methods to easily load a file or json data. ::

    from haralyzer import HarParser

    har_parser = HarParser.from_file("har_data.har)

    # Or

    with open("har-data.har), encoding="utf-8") as infile:
        data = infile.read()
    har_parser = HarParser.from_string(data)
