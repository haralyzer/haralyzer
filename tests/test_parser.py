import pytest
from har import HarParser


# This has two of each common content type as the values for each content-type
RESPONSE_HEADERS = ['content-length', 'content-encoding', 'accept-ranges',
                    'vary', 'connection', 'via', 'cache-control', 'date',
                    'content-type', 'age']

CONTENT_TYPES = ['application/json', 'application/javascript',
                 'audio/mp4', 'audio/mpeg',
                 'image/jpeg', '']


def test_init():
    # Make sure we only tolerate valid input
    with pytest.raises(ValueError):
        har_parser = HarParser(har_data='please_dont_work')
        assert har_parser


def test_match_headers(har_data):

    # The HarParser does not work without a full har file, but we only want
    # to test a piece, so this initial load is just so we can get the object
    # loaded.
    init_data = har_data('humanssuck.net.har')
    har_parser = HarParser(har_data=init_data)

    raw_headers = har_data('single_entry.har')

    # TEST THE REGEX FEATURE FIRST #

    # These should all be True
    test_data = {'request':
                    {'accept': '.*text/html,application/xhtml.*',
                     'host': 'humanssuck.*',
                     'accept-encoding': 'gzip, deflate',
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
