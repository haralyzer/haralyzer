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


def _load_test_data(har_data):
    """
    Loads the test files we need and returns them in the proper format.
    """
    har_data_1 = har_data('multi_test_1.har')
    har_data_2 = har_data('multi_test_2.har')
    har_data_3 = har_data('multi_test_3.har')
    return [har_data_1, har_data_2, har_data_3]
