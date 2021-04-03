HarPage
+++++++

The ``HarPage`` object contains most of the goods you need to easily analyze a
page. It has helper methods that are accessible, but most of the data you need is
in properties for easy access. You can create a HarPage object directly by giving
it the page ID (yes, I know it is stupid, it's just how HAR is organized), and either
a ``HarParser`` with `har_parser=parser`, or a ``dict`` representing the JSON of a full HAR
file (see example in HarParser) with `har_data=har_data`. ::

    import json
    from haralyzer import HarPage

    with open('har_data.har', 'r') as f:
        har_page = HarPage('page_3', har_data=json.loads(f.read()))

    ### GET BASIC INFO
    har_page.hostname
    # 'humanssuck.net'
    har_page.url
    # 'http://humanssuck.net/about/'

    ### WORK WITH LOAD TIMES (all load times are in ms) ###

    # Get image load time in milliseconds as rendered by the browser
    har_page.image_load_time
    # 713

    # We could do this with 'css', 'js', 'html', 'audio', or 'video'

    ### WORK WITH SIZES (all sizes are in bytes) ###

    # Get the total page size (with all assets)
    har_page.page_size
    # prints 2423765

    # Get the total image size
    har_page.image_size
    # prints 733488
    # We could do this with 'css', 'js', 'html', 'audio', or 'video'

    # Get duplicate requests (requests to the same URL 2 or more times) if any
    # har_page.duplicate_url_request
    # Returns a dict where the key is a string of the URL and the value is an int of the number
    # of requests to that URL. Only requests with 2 or more are included.
    # {'https://test.com/': 3}

    # Get the transferred sizes (works only with HAR files, generated with Chrome)
    har_page.page_size_trans
    har_page.image_size_trans
    har_page.css_size_trans
    har_page.text_size_trans
    har_page.js_size_trans
    har_page.audio_size_trans
    har_page.video_size_trans

*IMPORTANT NOTE* - Technically, the `page_id` attribute of a single entry in a
HAR file is optional. As such, if your HAR file contains entries that do not map
to a page, an additional page will be created with an ID of `unknown`. This
"fake page" will contain all such entries. Since it is not a real page, it does
not have attributes for things like time to first byte or page load, and will
return `None`.