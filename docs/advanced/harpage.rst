Advanced HARPage
================

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
    # This method can filter by:
    # * content_type ('application/json' for example)
    # * status_code ('200' for example)
    # * request_type ('GET' for example)
    # * http_version ('HTTP/1.1' for example)
    # * load_time__gt (Takes an int representing load time in milliseconds.
    #   Entries with a load time greater than this will be included in the
    #   results.)
    # Parameters that accept a string use a regex by default, but you can also force a literal string match by passing regex=False

    # Get the size of the collection we just made #
    collection_size = har_page.get_total_size(entries)

    # We can also access files by type with a property #
    for js_file in har_page.js_files:
        ... do stuff ....

    ### GETTING LOAD TIMES ###

    # Get the BROWSER load time for all images in the 2XX status code range #
    load_time = har_page.get_load_time(content_type='image.*', status_code='2.*')

    # Get the TOTAL load time for all images in the 2XX status code range #
    load_time = har_page.get_load_time(content_type='image.*', status_code='2.*', asynchronous=False)


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
                print('This would appear to be an image')
            ### MATCH REQUEST TYPE ###
            if har_parser.match_request_type(entry, 'GET'):
                print('This is a GET request')
            ### MATCH STATUS CODE ###
            if har_parser.match_status_code(entry, '2.*'):
                print('Looks like all is well in the world')