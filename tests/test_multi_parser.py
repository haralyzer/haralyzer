import pytest
from haralyzer import MultiHarParser, HarPage


def test_init(har_data):
    data = _load_test_data(har_data)
    # Test the default of it only caring about one page
    har_parser = MultiHarParser(har_data=data)
    for page in har_parser.pages:
        assert isinstance(page, HarPage)


def test_load_times(har_data):
    data = _load_test_data(har_data)
    # Test the default of it only caring about one page
    har_parser = MultiHarParser(har_data=data)
    # Test total load time averages
    assert har_parser.load_time_mean == 519.33
    assert har_parser.load_time_stdev == 10.79
    # Test time to first byte
    assert har_parser.time_to_first_byte == 70.0
    # Test specific asset type load averages
    assert har_parser.js_load_time == 149.33
    assert har_parser.css_load_time == 74.33
    assert har_parser.image_load_time == 379.0
    assert har_parser.html_load_time == 1


def _load_test_data(har_data):
    """
    Loads the test files we need and returns them in the proper format.
    """
    har_data_1 = har_data('multi_test_1.har')
    har_data_2 = har_data('multi_test_2.har')
    har_data_3 = har_data('multi_test_3.har')
    return [har_data_1, har_data_2, har_data_3]
