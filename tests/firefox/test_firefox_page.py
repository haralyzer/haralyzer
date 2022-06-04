"""Test Firefox Page"""
import re
import pytest
from haralyzer import HarPage, HarParser
from haralyzer.errors import PageNotFoundError

BAD_PAGE_ID = "sup_dawg"
PAGE_ID = "page_1"


def test_init(har_data):
    """
    Test the object loading
    """
    with pytest.raises(ValueError):
        assert HarPage(PAGE_ID)

    init_data = har_data("firefox.har")

    # Throws PageNotFoundException with bad page ID
    with pytest.raises(PageNotFoundError):
        assert HarPage(BAD_PAGE_ID, har_data=init_data)

    # Make sure it can load with either har_data or a parser
    page = HarPage(PAGE_ID, har_data=init_data)
    assert isinstance(page, HarPage)
    assert repr(page) == "ID: page_1, URL: https://www.jwhite.network/"
    parser = HarParser(init_data)
    page = HarPage(PAGE_ID, har_parser=parser)
    assert isinstance(page, HarPage)

    assert len(page.entries) == 50
    # Make sure that the entries are actually in order. Going a little bit
    # old school here.
    for index, _ in enumerate(page.entries):
        if index != len(page.entries) - 1:
            current_date = page.entries[index].startTime
            next_date = page.entries[index + 1].startTime
            assert current_date <= next_date


def test_filter_entries(har_data):
    """
    Tests ability to filter entries, with or without regex
    """
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)

    # Filter by request type only
    entries = page.filter_entries(request_type=".*ET")
    assert len(entries) == 39
    for entry in entries:
        assert entry.request.method == entry["request"]["method"] == "GET"

    # Filter by request type and content_type
    entries = page.filter_entries(request_type=".*ET", content_type="image.*")
    assert len(entries) == 11
    for entry in entries:
        assert entry.request.method == entry["request"]["method"] == "GET"
        for header in entry.request.headers:
            if header["name"] == "Content-Type":
                assert re.search("image.*", header["value"])

    # Filter by request type, content type, and status code
    entries = page.filter_entries(
        request_type=".*ET", content_type="image.*", status_code="2.*"
    )
    assert len(entries) == 11
    for entry in entries:
        assert entry.request.method == entry["request"]["method"] == "GET"
        assert re.search("2.*", str(entry.response.status))
        for header in entry.response.headers:
            if header["name"] == "Content-Type":
                assert re.search("image.*", header["value"])
        for header in entry["response"]["headers"]:
            if header["name"] == "Content-Type":
                assert re.search("image.*", header["value"])

    entries = page.filter_entries(request_type=".*ST")
    assert len(entries) == 11
    entries = page.filter_entries(request_type=".*ET", content_type="video.*")
    assert len(entries) == 0
    entries = page.filter_entries(
        request_type=".*ET", content_type="image.*", status_code="3.*"
    )
    assert len(entries) == 0


def test_get_load_time(har_data):
    """
    Tests HarPage.get_load_time()
    """
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)

    assert page.get_load_time(request_type="GET") == 955
    assert page.get_load_time(request_type="GET", asynchronous=False) == 2419
    assert page.get_load_time(content_type="image.*") == 526
    assert page.get_load_time(status_code="2.*") == 1116


def test_entries(har_data):
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)

    for entry in page.entries:
        assert entry.pageref == entry["pageref"] == page.page_id


def test_request_types(har_data):
    """
    Test request type filters
    """
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)

    # Check request type lists
    for req in page.get_requests:
        assert req.request.method == req["request"]["method"] == "GET"

    for req in page.post_requests:
        assert req.request.method == req["request"]["method"] == "POST"


def test_load_times(har_data):
    """
    This whole test really needs better sample data. I need to make a
    web page with like 2-3 of each asset type to really test the load times.
    """
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)
    # Check initial page load
    assert page.actual_page.request.url == "https://www.jwhite.network/"

    # Check initial page load times
    assert page.initial_load_time == 139
    assert page.content_load_time == 238
    # Check content type browser (async) load times
    assert page.image_load_time == 526
    assert page.css_load_time == 87
    assert page.js_load_time == 367
    assert page.html_load_time == 139
    assert page.page_load_time == 564
    # TODO - Need to get sample data for these types
    assert page.audio_load_time == 0
    assert page.video_load_time == 0


def test_time_to_first_byte(har_data):
    """
    Tests that TTFB is correctly reported as a property of the page.
    """
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)
    assert page.time_to_first_byte == 140


def test_hostname(har_data):
    """
    Makes sure that the correct hostname is returned.
    """
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)
    assert page.hostname == "www.jwhite.network"


def test_url(har_data):
    """
    Makes sure that the correct URL is returned.
    """
    init_data = har_data("firefox.har")
    page = HarPage(PAGE_ID, har_data=init_data)
    assert page.url == "https://www.jwhite.network/"
