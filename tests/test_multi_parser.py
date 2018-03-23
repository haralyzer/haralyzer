import pytest
from haralyzer import MultiHarParser, HarPage

PAGE_ID = 'page_3'


def test_init(har_data):
    data = _load_test_data(har_data, num_test_files=4)
    # Test the default of it only caring about one page
    har_parser = MultiHarParser(har_data=data)
    assert len(har_parser.pages) == 8
    for page in har_parser.pages:
        assert isinstance(page, HarPage)
    har_parser = MultiHarParser(har_data=data, page_id=PAGE_ID)
    assert len(har_parser.pages) == 3
    for page in har_parser.pages:
        assert isinstance(page, HarPage)


def test_load_times(har_data):
    data = _load_test_data(har_data)
    # Test the default of it only caring about one page
    har_parser = MultiHarParser(har_data=data)
    # Test total page load time averages
    assert har_parser.page_load_time == 519
    # Test time to first byte
    assert har_parser.time_to_first_byte == 70
    # Test specific asset type load averages
    assert har_parser.js_load_time == 149
    assert har_parser.css_load_time == 74
    assert har_parser.image_load_time == 379
    assert har_parser.html_load_time == 70
    # TODO - Get audio/video load time data
    assert har_parser.video_load_time == 0
    assert har_parser.audio_load_time == 0


def test_stdev(har_data):
    """
    Tests the get_stdev method
    """
    data = _load_test_data(har_data)
    har_parser = MultiHarParser(har_data=data)
    with pytest.raises(ValueError):
        har_parser.get_stdev('nonexistent')
    # Full page load time stdev
    assert har_parser.get_stdev('page') == 11
    # Time to first byte stdev
    assert har_parser.get_stdev('ttfb') == 10
    # Test specific asset standard deviation
    assert har_parser.get_stdev('js') == 6
    assert har_parser.get_stdev('css') == 4
    assert har_parser.get_stdev('image') == 4
    assert har_parser.get_stdev('html') == 10
    # TODO - Get audio/video load time data
    assert har_parser.get_stdev('video') == 0
    assert har_parser.get_stdev('audio') == 0


def _load_test_data(har_data, num_test_files=3):
    """
    Loads the test files we need and returns them in the proper format.

    :param num_test_files: Maximum number of test files to return.
    :type num_test_files: integer
    """
    results = []
    for i in range(1, num_test_files + 1):
        results.append(har_data('multi_test_{0}.har'.format(i)))
    return results
