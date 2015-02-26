import datetime
import dateutil
from dateutil import parser
assert parser
import pytest
from har import HarParser, HarPage


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


def test_match_headers(har_data):

    # The HarParser does not work without a full har file, but we only want
    # to test a piece, so this initial load is just so we can get the object
    # loaded, we don't care about the data in that HAR file.
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)

    raw_headers = har_data('single_entry.har')

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


def test_create_asset_timeline(har_data):
    """
    Tests the asset timeline function by making sure that it inserts one object
    correctly.
    """
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(init_data)

    entry = har_data('single_entry.har')

    # Get the datetime object of the start time and total load time
    time_key = dateutil.parser.parse(entry['startedDateTime'])
    load_time = int(entry['time'])

    asset_timeline = har_parser.create_asset_timeline([entry])

    # The number of entries in the timeline should match the load time
    assert len(asset_timeline) == load_time

    for t in range(1, load_time):
        assert time_key in asset_timeline
        assert len(asset_timeline[time_key]) == 1
        # Compare the dicts
        for key, value in entry.iteritems():
            assert asset_timeline[time_key][0][key] == entry[key]
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
    for req_type, data in test_data.iteritems():
        for header, value in data.iteritems():
            is_match = parser.match_headers(entry, req_type,
                                                header, value, regex=regex)
            if expects:
                assert is_match
            else:
                assert not is_match
