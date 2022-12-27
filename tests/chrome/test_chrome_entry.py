import pytest
from haralyzer import HarPage, HarEntry


PAGE_ID = "page_1"


def test_entry(har_data):
    """
    Tests that HarEntry class works
    """
    init_data = har_data("chrome.har")
    single_entry = HarPage(PAGE_ID, har_data=init_data).entries[1]
    assert isinstance(single_entry, HarEntry)
    assert str(single_entry) == "HarEntry for https://jwhite.network/"
    assert repr(single_entry) == "HarEntry for https://jwhite.network/"

    assert single_entry.cache == {}
    assert len(single_entry.cookies) == 0
    assert single_entry.pageref == "page_1"
    assert single_entry.port == 249
    assert single_entry.status == 301
    assert single_entry.secure is False
    assert single_entry.serverAddress == "104.27.152.17"
    assert single_entry.time == 110.02700000244658
    assert single_entry.timings == {
        "blocked": 0.5099999980302528,
        "dns": 0,
        "ssl": 36.527,
        "connect": 62.269,
        "send": 1.0060000000000002,
        "wait": 44.8429999964661,
        "receive": 1.3990000079502352,
        "_blocked_queueing": 0.5099999980302528,
    }
    assert single_entry.url == "https://jwhite.network/"


def test_request(har_data):
    """
    Tests that HarEntry.request has the correct data
    """
    init_data = har_data("chrome.har")
    request = HarPage(PAGE_ID, har_data=init_data).entries[1].request
    assert str(request) == "HarEntry.Request for https://jwhite.network/"
    assert repr(request) == "HarEntry.Request for https://jwhite.network/"

    assert (
        request.accept
        == "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    )
    assert request.cookies == [
        {
            "name": "__cfduid",
            "value": "df477fc1d24c2bbce2fe8127a020316a11598723802",
            "expires": None,
            "httpOnly": False,
            "secure": False,
        }
    ]
    assert request.bodySize == 0
    assert request.cacheControl == "no-cache"
    assert request.encoding == "gzip, deflate, br"
    assert len(request.headers) == 16
    assert request.headersSize == -1
    assert request.host is None
    assert request.httpVersion == "http/2.0"
    assert request.language == "en-US,en;q=0.9"
    assert request.method == "GET"
    assert len(request.queryString) == 0
    assert request.url == "https://jwhite.network/"
    assert (
        request.userAgent
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 "
        "Safari/537.36"
    )
    assert request.mimeType is None
    assert request.text is None

    assert request.get_header_value("Connection") is None


def test_request_post(har_data):
    """
    Tests that HarEntry.request has the correct POST data
    """
    init_data = har_data("chrome.har")
    request = HarPage(PAGE_ID, har_data=init_data).entries[30].request
    assert str(request) == "HarEntry.Request for https://jwhite.report-uri.com/r/d/csp/enforce"
    assert repr(request) == "HarEntry.Request for https://jwhite.report-uri.com/r/d/csp/enforce"

    assert request.accept == "*/*"
    assert request.cookies == []
    assert request.bodySize == 1034
    assert request.cacheControl == "no-cache"
    assert request.encoding == "gzip, deflate, br"
    assert len(request.headers) == 17
    assert request.headersSize == -1
    assert request.host is None
    assert request.httpVersion == "http/2.0"
    assert request.language == "en-US,en;q=0.9"
    assert request.method == "POST"
    assert len(request.queryString) == 0
    assert request.url == "https://jwhite.report-uri.com/r/d/csp/enforce"
    assert (
        request.userAgent
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 "
        "Safari/537.36"
    )
    assert request.mimeType == "application/csp-report"
    assert len(request.text) == 1034

    assert request.get_header_value("Connection") is None


def test_response(har_data):
    """
    Tests the HarEntry.response has the correct data
    """
    init_data = har_data("chrome.har")
    response = HarPage(PAGE_ID, har_data=init_data).entries[1].response
    assert response.bodySize == -1
    assert response.cacheControl == "max-age=3600"
    assert response.contentSecurityPolicy is None
    assert response.contentSize == 0
    assert response.contentType is None
    assert response.date == "Thu, 24 Sep 2020 22:22:57 GMT"
    assert len(response.headers) == 13
    assert response.headersSize == -1
    assert response.httpVersion == "http/2.0"
    assert response.lastModified is None
    assert response.mimeType == "x-unknown"
    assert response.redirectURL == "https://www.jwhite.network"
    assert response.status == 301
    assert response.statusText == ""
    with pytest.raises(KeyError):
        assert len(response.text)

    assert response.get_header_value("Server") == "cloudflare"


def test_backwards(har_data):
    """
    Tests that HarEntry class works if expecting dictionary.
    Made so it is a non-breaking change
    """
    init_data = har_data("chrome.har")
    single_entry = HarPage(PAGE_ID, har_data=init_data).entries[1]
    assert single_entry["cache"] == {}
    assert single_entry["pageref"] == "page_1"
    assert single_entry["connection"] == "249"
    with pytest.raises(KeyError):
        assert single_entry["_securityState"]
    assert single_entry["serverIPAddress"] == "104.27.152.17"
    assert single_entry["time"] == 110.02700000244658
    assert single_entry["timings"] == {
        "blocked": 0.5099999980302528,
        "dns": 0,
        "ssl": 36.527,
        "connect": 62.269,
        "send": 1.0060000000000002,
        "wait": 44.8429999964661,
        "receive": 1.3990000079502352,
        "_blocked_queueing": 0.5099999980302528,
    }
    assert single_entry["request"]["method"] == "GET"

    assert len(single_entry) == 12
    assert len(single_entry.keys()) == 12
    assert len(single_entry.items()) == 12

    assert single_entry.get("time") == 110.02700000244658
    assert single_entry.get("NothingHere", "Default") == "Default"

    assert single_entry.request["method"] == single_entry.request.get("method") == "GET"

    assert single_entry.response["status"] == single_entry.response.get("status") == 301

    # MISC TESTS FOR DICT COMPATIBILITY/COVERAGE
    single_entry["Testing"] = "HelloWorld"
    assert "Testing" in single_entry
    del single_entry["Testing"]
    assert iter(single_entry)
