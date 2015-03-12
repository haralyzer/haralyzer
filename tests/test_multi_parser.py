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
    assert har_parser.load_time_mean == 519.33
    assert har_parser.load_time_stdev == 10.79



def _load_test_data(har_data):
    """
    Loads the test files we need and returns them in the proper format.
    """
    har_data_1 = har_data('multi_test_1.har')
    har_data_2 = har_data('multi_test_2.har')
    har_data_3 = har_data('multi_test_3.har')
    return [har_data_1, har_data_2, har_data_3]
