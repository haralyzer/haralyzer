from datetime import datetime
import dateutil
import pytest
from har import HarPage, HarParser

PAGE_ID = 'page_03'

def test_init(har_data):
    """
    Test the object loading
    """
    with pytest.raises(ValueError):
        page = HarPage(PAGE_ID)

    # Make sure it can load with either har_data or a parser
    init_data = har_data('humanssuck.net.har')
    page = HarPage(PAGE_ID, har_data=init_data)
    assert isinstance(page, HarPage)
    parser = HarParser(init_data)
    page = HarPage(PAGE_ID, parser=parser)
    assert isinstance(page, HarPage)

    # Make sure that the entries are actually in order. Going a little bit
    # old school here.
    for index in range(0, len(page.entries)):
        if index != len(page.entries) - 1:
            current_date = dateutil.parser.parse(
                page.entries[index]['startedDateTime'])
            next_date = dateutil.parser.parse(
                page.entries[index + 1]['startedDateTime'])
            assert current_date <= next_date

def test_file_types(har_data):
    """
    Test file type properties
    """
    init_data = har_data('humanssuck.net.har')
    page = HarPage(har_data=init_data)

    file_types = {'image_files': 'image', 'css_files': 'css',
                  'js_files': 'javascript', 'audio_files': 'audio',
                  'video_files': 'video'}

    #for k, v in file_types.iteritems():
    #    for asset in getattr(h, k, None):
    #        assert _correct_file_type(asset, v)
    pass

def test_request_types(har_data):
    """
    Test request type filters
    """
    init_data = har_data('humanssuck.net.har')
    page = HarPage(har_data=init_data)

    # Check request type lists
    for req in page.get_requests:
        assert req['request']['method'] == 'GET'

    for req in page.post_requests:
        assert req['request']['method'] == 'POST'

def test_load_times(har_data):
    init_data = har_data('humanssuck.net.har')
    page = HarPage(har_data=init_data)
    pass
    # Check initial page load
    # assert h.initial_page['request']['url'] == 'http://humanssuck.net/'

    # Check initial page load times
    # assert h.load_time == 153
    # assert h.total_load_time == 567

    # Check sizes. Kind of lame, but the page sizes are hardcoded, and were
    # confirmed with other services that parse HAR files (like GTMetrix)
    # assert h.total_page_size == 62204


def _correct_file_type(entry, file_type):
    for header in entry['response']['headers']:
        if header['name'] == 'Content-Type':
            return file_type in header['value']
