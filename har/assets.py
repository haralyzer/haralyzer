import datetime
import dateutil
from dateutil import parser
assert parser
import re


class HarParser(object):

    def __init__(self, har_data=None):
        """
        A Basic HAR parser that also adds helpful stuff for analyzing the
        performance of a web page.

        :param har: a ``dict`` representing the JSON of a HAR file (i.e. - you
        need to load the HAR data into a string and use json.loads or
        requests.json() if you are pulling the data via HTTP.
        """
        if not har_data or not isinstance(har_data, dict):
            raise ValueError('A dict() representation of a HAR file is required'
                             ' to instantiate this class. Please RTFM.')
        self.har_data = har_data['log']

    def match_headers(self, entry, header_type, header, value, regex=True):
        """
        Tiny little helper function to match headers.

        Since the output of headers might use different case, like:

            'content-type' vs 'Content-Type'

        This function is case-insensitive

        :param entry: entry object
        :param header_type: ``str`` of header type. Valid values:

            * 'request'
            * 'response'

        :param header: ``str`` of the header to search for
        :param value: ``str`` of value to search for
        :param regex: ``bool`` indicating whether to use a regex for matching,
        or a literal string match.
        :returns: a ``bool`` indicating whether a match was found
        """
        if header_type not in entry:
            raise ValueError('Invalid header_type, should be either:\n\n'
                             '* \'request\'\n*\'response\'')

        for h in entry[header_type]['headers']:
            if h['name'].lower() == header.lower() and h['value'] is not None:
                if regex and re.search(value, h['value'], flags=re.IGNORECASE):
                    return True
                elif value == h['value']:
                    return True
        return False

    def match_request_type(self, entry, request_type, regex=True):
        """
        Helper function that returns request types based on the given regex

        :param entry: entry object to analyze
        :param request_type: ``str`` of request type to match
        :param regex: ``bool`` indicating whether to use a regex or string match
        """
        if regex:
            return re.search(request_type, entry['request']['method'],
                             flags=re.IGNORECASE) is not None
        else:
            return entry['request']['method'] == request_type

    def match_status_code(self, entry, status_code, regex=True):
        """
        Helper function that returns request types based on the given regex

        NOTE: This is doing a STRING comparison NOT NUMERICAL

        :param entry: entry object to analyze
        :param request_type: ``regex`` of request type to match
        """
        if regex:
            return re.search(status_code,
                             str(entry['response']['status'])) is not None
        else:
            return str(entry['response']['status']) == status_code

    def create_asset_timeline(self, asset_list):
        """
        Returns a ``dict`` of the timeline for the requested assets. The key is
        a datetime object (down to the millisecond) of ANY time where at least
        one of the requested assets was loaded. The value is a ``list`` of ALL
        assets that were loading at that time.

        :param asset_list: ``list`` of the assets to create a timeline for.
        """
        results = dict()
        # Return None if none of these assets were on the page
        if asset_list is None:
            return None
        for asset in asset_list:
            time_key = dateutil.parser.parse(asset['startedDateTime'])
            load_time = int(asset['time'])
            # Add the start time and asset to the results dict
            if time_key in results:
                results[time_key].append(asset)
            else:
                results[time_key] = [asset]
            # For each millisecond the asset was loading, insert the asset
            # into the appropriate key of the results dict. Starting the range()
            # index at 1 because we already inserted the first millisecond.
            for t in range(1, load_time):
                time_key = time_key + datetime.timedelta(milliseconds=1)
                if time_key in results:
                    results[time_key].append(asset)
                else:
                    results[time_key] = [asset]

        return results

    @property
    def pages(self):
        pages = []
        for har_page in self.har_data['pages']:
            page = HarPage(har_page['id'], parser=self)
            pages.append(page)

        return pages

    @property
    def browser(self):
        return self.har_data['browser']

    @property
    def version(self):
        return self.har_data['version']

    @property
    def creator(self):
        return self.har_data['creator']


class HarPage(object):

    def __init__(self, page_id, parser=None, har_data=None):
        """
        An object representing one page of a HAR resource

        :param page_id: ``str`` of the page ID
        :param parser: a HarParser object
        :param har_data: ``dict`` of a file HAR file
        """
        self.page_id = page_id
        if parser is None and har_data is None:
            raise ValueError('Either parser or har_data is required')
        if parser:
            self.parser = parser
        else:
            self.parser = HarParser(har_data=har_data)

        # Init properties that mimic the actual 'pages' object from the HAR file
        raw_data = self.parser.har_data
        for page in raw_data['pages']:
            if page['id'] == self.page_id:
                self.title = page['title']
                self.startedDateTime = page['startedDateTime']
                self.pageTimings = page['pageTimings']

    def filter_entries(self, request_type=None, content_type=None,
                       status_code=None, regex=True):
        """
        Returns a ``list`` of entry objects based on the filter criteria.

        :param request_type: ``str`` of request type (i.e. - GET or POST)
        :param content_type: ``str`` of regex to use for finding content type
        :param status_code: ``int`` of the desired status code
        :param regex: ``bool`` indicating whether this should be a regex match
        or an exact string match
        """
        results = []

        for entry in self.entries:
            """
            So yea... this is a bit ugly. We are looking for:

                * The request type using self._match_request_type()
                * The content type using self._match_headers()
                * The HTTP response status code using self._match_status_code()

            Oh lords of python.... please forgive my soul
            """
            valid_entry = True
            if request_type is not None:
                if not self.parser.match_request_type(
                    entry, request_type, regex=regex):
                    valid_entry = False
            if content_type is not None:
                if not self.parser.match_headers(
                    entry, 'response', 'Content-Type', content_type, regex=regex):
                    valid_entry = False
            if status_code is not None:
                if not self.parser.match_status_code(
                    entry, status_code, regex=regex):
                    valid_entry = False

            if valid_entry:
                results.append(entry)

        return results

    def get_load_time(self, request_type='.*', content_type='.*',
                      status_code='.*', async=True):
        """
        This method can return the TOTAL load time for the assets or the ACTUAL
        load time, the difference being that the actual load time takes
        asyncronys transactions into account. So, if you want the total load
        time, set async=False.

        EXAMPLE:

        I want to know the load time for images on a page that has two images,
        each of which took 2 seconds to download, but the browser downloaded
        them at the same time.

        self.get_load_time(content_types=['image']) (returns 2)
        self.get_load_time(content_types=['image'], async=False) (returns 4)
        """
        entries = self.filter_entries(request_type=request_type,
                                      content_type=content_type,
                                      status_code=status_code)

        if not async:
            time = 0
            for entry in entries:
                time += entry['time']
            return time
        else:
            return len(self.parser.create_asset_timeline(entries))

    @property
    def entries(self):
        page_entries = []
        for entry in self.parser.har_data['entries']:
            if entry['pageref'] == self.page_id:
                page_entries.append(entry)
        # Make sure the entries are sorted chronologically
        return sorted(page_entries,
                      key=lambda entry: entry['startedDateTime'])

    @property
    def get_requests(self):
        """
        Returns a list of GET requests, each of which is an 'entry' data object
        """
        return self.filter_entries(request_type='get')

    @property
    def post_requests(self):
        """
        Returns a list of POST requests, each of which is an 'entry' data object
        """
        return self.filter_entries(request_type='post')

    @property
    def image_files(self):
        """
        Returns a list of images, each of which is an 'entry' data object.
        """
        return self.filter_entries(content_type='image')

    @property
    def css_files(self):
        """
        Returns a list of css files, each of which is an 'entry' data object.
        """
        return self.filter_entries(content_type='css')

    @property
    def js_files(self):
        """
        Returns a list of javascript files, each of which is an 'entry'
        data object.
        """
        return self.filter_entries(content_type='javascript')

    @property
    def html_files(self):
        """
        Returns a list of all HTML elements, each of which is an entry object.
        """
        return self.filter_entries(content_type='html')

    @property
    def audio_files(self):
        """
        Returns a list of all HTML elements, each of which is an entry object.
        """
        return self.filter_entries(content_type='audio')

    @property
    def video_files(self):
        """
        Returns a list of all HTML elements, each of which is an entry object.
        """
        return self.filter_entries(content_type='video')

    @property
    def actual_page(self):
        """
        Returns the first entry object that does not have a redirect status,
        indicating that it is the actual page we care about (after redirects).
        """
        for entry in self.entries:
            if not (entry['response']['status'] >= 300 and
                    entry['response']['status'] <= 399):
                return entry

    @property
    def page_size(self):
        """
        Returns the size (in bytes) of the first non-redirect page
        """
        # The initial request should always be the first one in the list that
        # does not redirect
        return self.actual_page['response']['bodySize']

    @property
    def total_page_size(self):
        """
        Returns the total page size (in bytes) including all assets
        """
        size = 0
        for entry in self.entries:
            if entry['response']['bodySize'] and \
                    entry['response']['bodySize'] > 0:
                size += entry['response']['bodySize']
        return size

    @property
    def content_load_time(self):
        """
        Returns the full load time (in bytes) of the page itself
        """
        # Assuming for right now that the HAR file is only for one page
        return self.pageTimings['onContentLoad']

    @property
    def total_load_time(self):
        """
        Returns the full load time (in bytes) of all assets on the page
        """
        # Assuming for right now that the HAR file is only for one page
        return self.pageTimings['onLoad']

    @property
    def image_load_time(self, async=True):
        """
        Returns the total load time for all images.
        """
        return self.get_load_time(content_type='image', async=async)

    @property
    def css_load_time(self, async=True):
        """
        Returns the total load time for all CSS files.
        """
        return self.get_load_time(content_type='css', async=async)

    @property
    def js_load_time(self, async=True):
        """
        Returns the total load time for all javascript files.
        """
        return self.get_load_time(content_type='javascript', async=async)

    @property
    def html_load_time(self, async=True):
        """
        Returns the total load time for all html files.
        """
        return self.get_load_time(content_type='html', async=async)

    @property
    def audio_load_time(self, async=True):
        return self.get_load_time(content_type='audio', async=async)

    @property
    def video_load_time(self, async=True):
        return self.get_load_time(content_type='video', async=async)
