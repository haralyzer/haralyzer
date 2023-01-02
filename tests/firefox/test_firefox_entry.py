from haralyzer import HarPage, HarEntry


PAGE_ID = "page_1"


def test_entry(har_data):
    """
    Tests that HarEntry class works
    """
    init_data = har_data("firefox.har")
    single_entry = HarPage(PAGE_ID, har_data=init_data).entries[0]
    assert isinstance(single_entry, HarEntry)
    assert str(single_entry) == "HarEntry for https://www.jwhite.network/"
    assert repr(single_entry) == "HarEntry for https://www.jwhite.network/"

    assert single_entry.cache == {}
    assert len(single_entry.cookies) == 0
    assert single_entry.pageref == "page_1"
    assert single_entry.port == 443
    assert single_entry.status == 200
    assert single_entry.secure is True
    assert single_entry.serverAddress == "104.27.153.17"
    assert single_entry.time == 139
    assert single_entry.timings == {
        "receive": 0,
        "send": 0,
        "connect": 34,
        "dns": 0,
        "wait": 67,
        "blocked": 39,
        "ssl": -1,
    }
    assert single_entry.url == "https://www.jwhite.network/"


def test_request(har_data):
    """
    Tests that HarEntry.request has the correct data
    """
    init_data = har_data("firefox.har")
    request = HarPage(PAGE_ID, har_data=init_data).entries[0].request
    assert str(request) == "HarEntry.Request for https://www.jwhite.network/"
    assert repr(request) == "HarEntry.Request for https://www.jwhite.network/"

    assert (
        request.accept
        == "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    )
    assert request.cookies == [
        {"name": "__cfduid", "value": "d3fc1e767b40bb39143a4d034497b56871600986075"}
    ]
    assert request.bodySize == 0
    assert request.cacheControl == "no-cache"
    assert request.encoding == "gzip, deflate, br"
    assert len(request.headers) == 10
    assert request.headersSize == 448
    assert request.host == "www.jwhite.network"
    assert request.httpVersion == "HTTP/2"
    assert request.language == "en-US,en;q=0.5"
    assert request.method == "GET"
    assert len(request.queryString) == 0
    assert request.url == "https://www.jwhite.network/"
    assert (
        request.userAgent
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"
    )
    assert request.mimeType is None
    assert request.text is None

    assert request.get_header_value("Connection") == "keep-alive"


def test_request_post(har_data):
    """
    Tests that HarEntry.request has the correct POST data
    """
    init_data = har_data("firefox.har")
    request = HarPage(PAGE_ID, har_data=init_data).entries[26].request
    assert str(request) == "HarEntry.Request for https://jwhite.report-uri.com/r/d/csp/enforce"
    assert repr(request) == "HarEntry.Request for https://jwhite.report-uri.com/r/d/csp/enforce"

    assert request.accept == "*/*"
    assert request.cookies == []
    assert request.bodySize == 929
    assert request.cacheControl is None
    assert request.encoding == "gzip, deflate, br"
    assert len(request.headers) == 9
    assert request.headersSize == 356
    assert request.host == "jwhite.report-uri.com"
    assert request.httpVersion == "HTTP/2"
    assert request.language == "en-US,en;q=0.5"
    assert request.method == "POST"
    assert len(request.queryString) == 0
    assert request.url == "https://jwhite.report-uri.com/r/d/csp/enforce"
    assert (
        request.userAgent
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"
    )
    assert request.mimeType == "application/csp-report"
    assert len(request.text) == 929

    assert request.get_header_value("Connection") == "keep-alive"


def test_response(har_data):
    """
    Tests the HarEntry.response has the correct data
    """
    init_data = har_data("firefox.har")
    response = HarPage(PAGE_ID, har_data=init_data).entries[0].response
    assert response.bodySize == 7887
    assert response.cacheControl == "max-age=31536000"
    assert len(response.contentSecurityPolicy) == 654
    assert response.contentSize == 18992
    assert response.contentType == "text/html; charset=utf-8"
    assert response.date == "Thu, 24 Sep 2020 22:21:46 GMT"
    assert len(response.headers) == 29
    assert response.headersSize == 2316
    assert response.httpVersion == "HTTP/2"
    assert response.lastModified == "Sat, 29 Aug 2020 20:36:06 GMT"
    assert response.mimeType == "text/html; charset=utf-8"
    assert response.redirectURL == ""
    assert response.status == 200
    assert response.statusText == "OK"
    # It needs to be able to be two values as locally I tested and got 18989 but travis.ci gets 18960
    # TODO: Figure out why this is happening and correct it
    assert len(response.text) in [18989, 18960]
    assert len(response.text) == 18960

    assert response.get_header_value("Server") == "cloudflare"


def test_response_encoded(har_data):
    """
    Tests the HarEntry.response has the correct data with encoded content
    """
    init_data = har_data("firefox.har")
    response = HarPage(PAGE_ID, har_data=init_data).entries[9].response
    assert response.bodySize == 33902
    assert response.cacheControl == "max-age=31536000"
    assert len(response.contentSecurityPolicy) == 654
    assert response.contentSize == 31485
    assert response.contentType == "image/png"
    assert response.date == "Thu, 24 Sep 2020 22:21:47 GMT"
    assert len(response.headers) == 32
    assert response.headersSize == 2417
    assert response.httpVersion == "HTTP/2"
    assert response.lastModified == "Sat, 29 Aug 2020 20:36:06 GMT"
    assert response.mimeType == "image/png"
    assert response.redirectURL == ""
    assert response.status == 200
    assert response.statusText == "OK"
    assert len(response.text) == 41980
    assert response.textEncoding == "base64"

    assert response.get_header_value("Server") == "cloudflare"


def test_backwards(har_data):
    """
    Tests that HarEntry class works if expecting dictionary.
    Made so it is a non-breaking change
    """
    init_data = har_data("firefox.har")
    single_entry = HarPage(PAGE_ID, har_data=init_data).entries[0]
    assert single_entry["cache"] == {}
    assert single_entry["pageref"] == "page_1"
    assert single_entry["connection"] == "443"
    assert single_entry["_securityState"] == "secure"
    assert single_entry["serverIPAddress"] == "104.27.153.17"
    assert single_entry["time"] == 139
    assert single_entry["timings"] == {
        "receive": 0,
        "send": 0,
        "connect": 34,
        "dns": 0,
        "wait": 67,
        "blocked": 39,
        "ssl": -1,
    }
    assert single_entry["request"]["method"] == "GET"

    assert len(single_entry) == 10
    assert len(single_entry.keys()) == 10
    assert len(single_entry.items()) == 10

    assert single_entry.get("time") == 139
    assert single_entry.get("NothingHere", "Default") == "Default"

    assert single_entry.request["method"] == single_entry.request.get("method") == "GET"

    assert single_entry.response["status"] == single_entry.response.get("status") == 200

    # MISC TESTS FOR DICT COMPATIBILITY/COVERAGE
    single_entry["Testing"] = "HelloWorld"
    assert "Testing" in single_entry
    del single_entry["Testing"]
    assert iter(single_entry)
