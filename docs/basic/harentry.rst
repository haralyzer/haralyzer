HarEntry
++++++++

The ``HarEntry()`` object contains useful information for each request. The main purpose is to have easy of use as it has a lot of attributes.
Each entry also contains a ``Request()`` and ``Response()`` which are styled off of the requests library.::

    import json
    from haralyzer import HarPage

    with open("humanssuck.net.har", 'r') as f:
        har_page = HarPage('page_3', har_data=json.loads(f.read()))

    ### GET BASIC INFO
    print(har_page.hostname)
    # 'humanssuck.net'
    print(har_page.url)
    # 'http://humanssuck.net/'

    ### GET LIST OF ENTRIES
    print(har_page.entries)
    # [HarEntry for http://humanssuck.net/, HarEntry for http://humanssuck.net/test.css, ...]

    ### WORKING WITH ENTRIES
    single_entry = har_page.entries[0]

    ### REQUEST HEADERS
    print(single_entry.request.headers)
    # {'host': 'humanssuck.net', 'user-agent': 'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:25.0) Gecko/20100101 Firefox/25.0', ...}

    ### RESPONSE HEADERS
    print(single_entry.response.headers)
    # {'server': 'nginx', 'date': 'Mon, 23 Feb 2015 03:28:12 GMT', ...}

    ### RESPONSE CODE
    print(single_entry.response.status)
    # 200

    # GET THE VALUE OF A REQUEST OR RESPONSE HEADER
    print(single_entry.request.headers.get("accept"))
    # text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

    # ALL ATTRIBUTES OF A ENTRY

    single_entry.cache
    # Dictionary of cached content
    single_entry.cookies
    # List of combined cookies for request and response
    single_entry.pageref
    # String of the pageref
    single_entry.port
    # Integer of the port number for the server
    single_entry.request
    # Request object
    single_entry.response
    # Response object
    single_entry.secure
    # Bool if secure is set
    single_entry.serverAddress
    # String of the server IP
    single_entry.startTime
    # Datetime of the start time
    single_entry.time
    # Integer of total time for entry
    single_entry.timings
    # Dictionary of the timings for a request
    single_entry.url
    # String of the request url

    # ALL ATTRIBUTES OF A REQUEST

    single_entry.request.accept
    # String of the ``Accept`` header
    single_entry.request.bodySize
    # Integer of the body size for the request
    single_entry.request.cacheControl
    # String of the ``Cache-Control`` header
    single_entry.request.cookies
    # List of cookies
    single_entry.request.encoding
    # String of the ``Accept-Encoding`` header
    single_entry.request.headers
    # Dictionary of headers
    single_entry.request.headersSize
    # Integer of the size of the headers
    single_entry.request.host
    # String of the ``Host`` header
    single_entry.request.httpVersion
    # String of the http version used
    single_entry.request.language
    # String of the ``Accept-Language`` header
    single_entry.request.method
    # String of the HTTP method used
    single_entry.request.queryString
    # List of query string used
    single_entry.request.url
    # String of the URL
    single_entry.request.userAgent
    # String of the User-Agent

    ### ALL ATTRIBUTES OF A RESPONSE
    single_entry.response.bodySize
    # Integer of the body size for the response
    single_entry.response.cacheControl
    # String of the `Cache-Control` header
    single_entry.response.contentSecurityPolicy
    # String of the `Content-Security-Policy`` header
    single_entry.response.contentSize
    # Integer of the content size
    single_entry.response.contentType
    # String of the ``content-type`` header
    single_entry.response.date
    # String of the ``date`` header
    single_entry.response.headers
    # Dictionary of headers
    single_entry.response.headersSize
    # Integer of the size of the headers
    single_entry.response.httpVersion
    # String of the http version used
    single_entry.response.lastModified
    # String of the ``last-modified`` header
    single_entry.response.mimeType
    # String of the mimeType of the content
    single_entry.response.redirectURL
    # String of the redirect URL or None
    single_entry.response.status
    # Integer of th HTTP status code
    single_entry.response.statusText
    # String of HTTP status
    single_entry.response.text
    # String of content received

    # You are still able to access items like a dictionary.
    print(single_entry["connection"])
    # "80"
