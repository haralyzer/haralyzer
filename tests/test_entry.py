from haralyzer import HarPage, HarEntry
from datetime import datetime


PAGE_ID = 'page_3'


def test_entry(har_data):
    init_data = har_data('humanssuck.net.har')
    single_entry = HarPage(PAGE_ID, har_data=init_data).entries[0]
    assert isinstance(single_entry, HarEntry)
    assert single_entry.cache == {}
    assert len(single_entry.cookies) == 0
    assert len(single_entry.headers) == 17
    assert single_entry.pageref == "page_3"
    assert single_entry.port == 80
    assert single_entry.status == 200
    assert single_entry.secure is None
    assert single_entry.server_address == "216.70.110.121"
    assert single_entry.time == 153
    assert single_entry.timings == {'receive': 0, 'send': 0, 'connect': 0, 'dns': 0, 'wait': 76, 'blocked': 77}


def test_request(har_data):
    init_data = har_data('humanssuck.net.har')
    request = HarPage(PAGE_ID, har_data=init_data).entries[0].request
    assert request.accept == "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
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
    init_data = har_data('humanssuck.net.har')
    response = HarPage(PAGE_ID, har_data=init_data).entries[0].response
    assert response.bodySize == 238
    assert response.cacheControl is None
    assert response.contentSecurityPolicy is None
    assert response.contentSize == 308
    assert response.contentType == "text/html; charset=UTF-8"
    assert isinstance(response.date, str)
    assert len(response.headers) == 11
    assert response.headersSize == 338
    assert response.httpVersion == "HTTP/1.1"
    assert response.lastModified == "Mon, 23 Feb 2015 03:22:35 GMT"
    assert response.mimeType == "text/html"
    assert response.redirectURL is None
    assert response.status == 200
    assert response.statusText == "OK"
    assert len(response.text) == 308

    assert response.get_header_value("Server") == "nginx"
