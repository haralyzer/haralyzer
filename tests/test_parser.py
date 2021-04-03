import datetime
import pytest
from haralyzer import HarParser, HarPage, HarEntry
from dateutil import parser as du


# This has two of each common content type as the values for each content-type
RESPONSE_HEADERS = ['content-length', 'content-encoding', 'accept-ranges',
                    'vary', 'connection', 'via', 'cache-control', 'date',
                    'content-type', 'age']

CONTENT_TYPES = ['application/json', 'application/javascript',
                 'audio/mp4', 'audio/mpeg',
                 'image/jpeg', '']


def test_init(har_data):
    # Make sure we only tolerate valid input
    with pytest.raises(ValueError):
        har_parser = HarParser('please_dont_work')
        assert har_parser

    har_data = har_data('humanssuck.net.har')
    har_parser = HarParser(har_data)
    for page in har_parser.pages:
        assert isinstance(page, HarPage)

    assert har_parser.browser == {'name': 'Firefox', 'version': '25.0.1'}
    assert har_parser.version == '1.1'
    assert har_parser.creator == {'name': 'Firebug', 'version': '1.12'}
    assert har_parser.hostname == 'humanssuck.net'


def test_init_entry_with_no_pageref(har_data):
    '''
    If we find an entry with no pageref it should end up in a HarPage object
    with page ID of unknown
    '''
    data = har_data('missing_pageref.har')
    har_parser = HarParser(data)
    # We should have two pages. One is defined in the pages key of the har file
    # but has no entries. The other should be our unknown page, with a single
    # entry
    assert len(har_parser.pages) == 2
    page = [p for p in har_parser.pages if p.page_id == 'unknown'][0]
    assert len(page.entries) == 1


def test_match_headers(har_data):

    # The HarParser does not work without a full har file, but we only want
    # to test a piece, so this initial load is just so we can get the object
    # loaded, we don't care about the data in that HAR file.
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)

    raw_headers = har_data('single_entry.har')

    # Make sure that bad things happen if we don't give it response/request
    test_data = {'captain beefheart':
                    {'accept': '.*text/html,application/xhtml.*',
                     'host': 'humanssuck.*',
                     'accept-encoding': '.*deflate',
                     },
                 }
    with pytest.raises(ValueError):
        _headers_test(har_parser, raw_headers, test_data, True, True)

    # TEST THE REGEX FEATURE FIRST #

    # These should all be True
    test_data = {'request':
                    {'accept': '.*text/html,application/xhtml.*',
                     'host': 'humanssuck.*',
                     'accept-encoding': '.*deflate',
                     },
                 'response':
                    {'server': 'nginx',
                     'content-type': 'text.*',
                     'connection': '.*alive',
                     },
                 }

    _headers_test(har_parser, raw_headers, test_data, True, True)

    test_data = {'request':
                    {'accept': '.*text/xml,application/xhtml.*',
                     'host': 'humansrule.*',
                     'accept-encoding': 'i dont accept that',
                     },
                 'response':
                    {'server': 'apache',
                     'content-type': 'application.*',
                     'connection': '.*dead',
                     },
                 }

    _headers_test(har_parser, raw_headers, test_data, False, True)

    # Test literal string matches #

    # These should all be True
    test_data = {'request':
                    {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     'host': 'humanssuck.net',
                     'accept-encoding': 'gzip, deflate',
                     },
                 'response':
                    {'server': 'nginx',
                     'content-type': 'text/html; charset=UTF-8',
                     'connection': 'keep-alive',
                     },
                 }

    _headers_test(har_parser, raw_headers, test_data, True, False)

    test_data = {'request':
                    {'accept': 'I accept nothing',
                     'host': 'humansrule.guru',
                     'accept-encoding': 'i dont accept that',
                     },
                 'response':
                    {'server': 'apache',
                     'content-type': 'your mom',
                     'connection': 'not keep-alive',
                     },
                 }

    _headers_test(har_parser, raw_headers, test_data, False, False)


def test_match_request_type(har_data):
    """
    Tests the ability of the parser to match a request type.
    """
    # The HarParser does not work without a full har file, but we only want
    # to test a piece, so this initial load is just so we can get the object
    # loaded, we don't care about the data in that HAR file.
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)

    entry = har_data('single_entry.har')

    # TEST THE REGEX FEATURE FIRST #
    assert har_parser.match_request_type(entry, '.*ET')
    assert not har_parser.match_request_type(entry, '.*ST')
    # TEST LITERAL STRING MATCH #
    assert har_parser.match_request_type(entry, 'GET', regex=False)
    assert not har_parser.match_request_type(entry, 'POST', regex=False)


def test_match_status_code(har_data):
    """
    Tests the ability of the parser to match status codes.
    """
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)

    entry = har_data('single_entry.har')

    # TEST THE REGEX FEATURE FIRST #
    assert har_parser.match_status_code(entry, '2.*')
    assert not har_parser.match_status_code(entry, '3.*')
    # TEST LITERAL STRING MATCH #
    assert har_parser.match_status_code(entry, '200', regex=False)
    assert not har_parser.match_status_code(entry, '201', regex=False)


def test_http_version(har_data):
    """
    Tests the ability of the parser to match status codes.
    """
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)

    entry = HarEntry(har_data('single_entry.har'))

    # TEST THE REGEX FEATURE FIRST #
    assert har_parser.match_http_version(entry, '.*1.1')
    assert not har_parser.match_http_version(entry, '.*2')
    # TEST LITERAL STRING MATCH #
    assert har_parser.match_http_version(entry, 'HTTP/1.1', regex=False)
    assert not har_parser.match_http_version(entry, 'HTTP/2.0', regex=False)


def test_match_content_type(har_data):
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)
    entry = HarEntry(har_data('single_entry.har'))
    assert har_parser.match_content_type(entry, content_type="text/html", regex=False)


def test_create_asset_timeline(har_data):
    """
    Tests the asset timeline function by making sure that it inserts one object
    correctly.
    """
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)

    entry = HarEntry(har_data('single_entry.har'))

    # Get the datetime object of the start time and total load time
    time_key = entry.startTime
    load_time = entry.time

    asset_timeline = har_parser.create_asset_timeline([entry])

    # The number of entries in the timeline should match the load time
    assert len(asset_timeline) == load_time

    for t in range(1, load_time):
        assert time_key in asset_timeline
        assert len(asset_timeline[time_key]) == 1
        # Compare the dicts
        for key, _ in asset_timeline.items():
            assert du.parse(asset_timeline[time_key][0].raw_entry["startedDateTime"]) == entry.startTime
        time_key = time_key + datetime.timedelta(milliseconds=1)


def _headers_test(parser, entry, test_data, expects, regex):
    """
    Little helper function to test headers matches

    :param parser: Instance of HarParser object
    :param entry: entry object
    :param test_data: ``dict`` of test data
    :param expects: ``bool`` indicating whether the assertion
    should be True/False
    :param regex: ``bool`` indicating whether we should be using regex
    search
    """
    for req_type, data in test_data.items():
        for header, value in data.items():
            is_match = parser.match_headers(
                entry, req_type, header, value, regex=regex)
            if expects:
                assert is_match
            else:
                assert not is_match
