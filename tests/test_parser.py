from har import HarParser


def test_parser(har_data):
    har_data = har_data('cnn.har')
    h = HarParser(har_data=har_data)

    # Check element type properties
    for img in h.images:
        assert _correct_file_type(img, 'image')

    for css in h.css_files:
        assert _correct_file_type(css, 'css')

    for js in h.js_files:
        assert _correct_file_type(js, 'javascript')

    # Check request type lists
    for req in h.get_requests:
        assert req['request']['method'] == 'GET'

    for req in h.post_requests:
        assert req['request']['method'] == 'POST'

    # Check initial page load
    assert h.initial_page['request']['url'] == 'http://www.cnn.com/'

    # Check initial page load times
    assert h.load_time == 1574
    assert h.total_load_time == 11288

    # Check sizes. Kind of lame, but the page sizes are hardcoded, and were
    # confirmed with other services that parse HAR files (like GTMetrix)
    assert h.total_page_size == 2423765

def _correct_file_type(entry, file_type):
    for header in entry['response']['headers']:
        print header
        if header['name'] == 'Content-Type':
            return file_type in header['value']
