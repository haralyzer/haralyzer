import pytest
from haralyzer import HarPage, HarEntry


PAGE_ID = 'page_3'


def test_entry(har_data):
    """
        Tests that HarEntry class works
    """
    init_data = har_data('humanssuck.net.har')
    single_entry = HarPage(PAGE_ID, har_data=init_data).entries[0]
    assert isinstance(single_entry, HarEntry)
    assert str(single_entry) == "HarEntry for http://humanssuck.net/"
    assert repr(single_entry) == "HarEntry for http://humanssuck.net/"

    assert single_entry.cache == {}
    assert len(single_entry.cookies) == 0
    assert single_entry.pageref == "page_3"
    assert single_entry.port == 80
    assert single_entry.status == 200
    assert single_entry.secure is False
    assert single_entry.serverAddress == "216.70.110.121"
    assert single_entry.time == 153
    assert single_entry.timings == {'receive': 0, 'send': 0, 'connect': 0, 'dns': 0, 'wait': 76, 'blocked': 77}
    assert single_entry.url == "http://humanssuck.net/"


def test_request(har_data):
    """
        Tests that HarEntry.request has the correct data
    """
    init_data = har_data('humanssuck.net.har')
    request = HarPage(PAGE_ID, har_data=init_data).entries[0].request
    assert str(request) == "HarEntry.Request for http://humanssuck.net/"
    assert repr(request) == "HarEntry.Request for http://humanssuck.net/"

    assert request.accept == "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    assert request.cookies == []
    assert request.bodySize == -1
    assert request.cacheControl is None
    assert request.encoding == "gzip, deflate"
    assert len(request.headers) == 6
    assert request.headersSize == 292
    assert request.host == "humanssuck.net"
    assert request.httpVersion == "HTTP/1.1"
    assert request.language == "en-US,en;q=0.5"
    assert request.method == "GET"
    assert len(request.queryString) == 0
    assert request.url == "http://humanssuck.net/"
    assert request.userAgent == "Mozilla/5.0 (X11; Linux i686 on x86_64; rv:25.0) Gecko/20100101 Firefox/25.0"

    assert request.get_header_value("Connection") == "keep-alive"


def test_response(har_data):
    """
        Tests the HarEntry.response has the correct data
    """
    init_data = har_data('humanssuck.net.har')
    response = HarPage(PAGE_ID, har_data=init_data).entries[0].response
    assert response.bodySize == 238
    assert response.cacheControl is None
    assert response.contentSecurityPolicy is None
    assert response.contentSize == 308
    assert response.contentType == "text/html; charset=UTF-8"
    assert response.date == "Mon, 23 Feb 2015 03:28:12 GMT"
    assert len(response.headers) == 11
    assert response.headersSize == 338
    assert response.httpVersion == "HTTP/1.1"
    assert response.lastModified == "Mon, 23 Feb 2015 03:22:35 GMT"
    assert response.mimeType == "text/html"
    assert response.redirectURL == ""
    assert response.status == 200
    assert response.statusText == "OK"
    assert len(response.text) == 308

    assert response.get_header_value("Server") == "nginx"


def test_backwards(har_data):
    """
        Tests that HarEntry class works if expecting dictionary.
        Made so it is a non-breaking change
    """
    init_data = har_data('humanssuck.net.har')
    single_entry = HarPage(PAGE_ID, har_data=init_data).entries[0]
    assert single_entry["cache"] == {}
    assert single_entry["pageref"] == "page_3"
    assert single_entry["connection"] == "80"
    with pytest.raises(KeyError):
        assert single_entry["_securityState"]
    assert single_entry["serverIPAddress"] == "216.70.110.121"
    assert single_entry["time"] == 153
    assert single_entry["timings"] == {'receive': 0, 'send': 0, 'connect': 0, 'dns': 0, 'wait': 76, 'blocked': 77}
    assert single_entry["request"]["method"] == "GET"

    assert len(single_entry) == 9
    assert len(single_entry.keys()) == 9
    assert len(single_entry.items()) == 9

    assert single_entry.get("time") == 153
    assert single_entry.get("NothingHere", "Default") == "Default"

    assert single_entry.request["method"] == single_entry.request.get("method") == "GET"

    assert single_entry.response["status"] == single_entry.response.get("status") == 200

    # MISC TESTS FOR DICT COMPATIBILITY/COVERAGE
    single_entry["Testing"] = "HelloWorld"
    assert "Testing" in single_entry
    del single_entry["Testing"]
    assert iter(single_entry)
