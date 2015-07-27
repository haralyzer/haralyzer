"""
Provides all of the main functional classes for analyzing HAR files
"""

from cached_property import cached_property
import datetime
import dateutil
# I know this import is stupid, but I cannot use dateutil.parser without it
from dateutil import parser
import numpy
assert parser
import re

from haralyzer.compat import iteritems


DECIMAL_PRECISION = 0


class HarParser(object):
    """
    A Basic HAR parser that also adds helpful stuff for analyzing the
    performance of a web page.
    """

    def __init__(self, har_data=None):
        """
        :param har_data: a ``dict`` representing the JSON of a HAR file
        (i.e. - you need to load the HAR data into a string using json.loads or
        requests.json() if you are pulling the data via HTTP.
        """
        if not har_data or not isinstance(har_data, dict):
            raise ValueError('A dict() representation of a HAR file is required'
                             ' to instantiate this class. Please RTFM.')
        self.har_data = har_data['log']

    def match_headers(self, entry, header_type, header, value, regex=True):
        """
        Function to match headers.

        Since the output of headers might use different case, like:

            'content-type' vs 'Content-Type'

        This function is case-insensitive

        :param entry: entry object
        :param header_type: ``str`` of header type. Valid values:

            * 'request'
            * 'response'

        :param header: ``str`` of the header to search for
        :param value: ``str`` of value to search for
        :param regex: ``bool`` indicating whether to use regex or exact match

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
        Helper function that returns entries with a request type
        matching the given `request_type` argument.

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
        Helper function that returns entries with a status code matching
        then given `status_code` argument.

        NOTE: This is doing a STRING comparison NOT NUMERICAL

        :param entry: entry object to analyze
        :param status_code: ``str`` of status code to search for
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
            for _ in range(1, load_time):
                time_key = time_key + datetime.timedelta(milliseconds=1)
                if time_key in results:
                    results[time_key].append(asset)
                else:
                    results[time_key] = [asset]

        return results

    @property
    def pages(self):
        """
        This is a list of HarPage objects, each of which represents a page
        from the HAR file.
        """
        pages = []
        for har_page in self.har_data['pages']:
            page = HarPage(har_page['id'], har_parser=self)
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

    @cached_property
    def hostname(self):
        return self.pages[0].hostname


class MultiHarParser(object):
    """
    An object that represents multiple HAR files OF THE SAME CONTENT.
    It is used to gather overall statistical data in situations where you have
    multiple runs against the same web asset, which is common in performance
    testing.
    """

    def __init__(self, har_data, page_id=None,
                 decimal_precision=DECIMAL_PRECISION):
        """
        :param har_data: A ``list`` of ``dict`` representing the JSON
        of a HAR file. See the docstring of HarParser.__init__ for more detail.
        :param page_id: IF a ``str`` of the page ID is provided, the
        multiparser will return aggregate results for this specific page. If
        not, it will assume that there is only one page in the run (this was
        written specifically for that use case).
        :param decimal_precision: ``int`` representing the precision of the
        return values for the means and standard deviations provided by this
        class.
        """
        self.har_data = har_data
        self.page_id = page_id
        self.decimal_precision = decimal_precision

    def get_load_times(self, asset_type):
        """
        Just a ``list`` of the load times of a certain asset type for each page

        :param asset_type: ``str`` of the asset to type to return load times for
        """
        load_times = []
        search_str = '{0}_load_time'.format(asset_type)
        for har_page in self.pages:
            val = getattr(har_page, search_str, None)
            load_times.append(val)
        return load_times

    def get_stdev(self, asset_type):
        """
        Returns the standard deviation for a set of a certain asset type.

        :param asset_type: ``str`` of the asset type to calculate standard
        deviation for.
        :returns: A ``int`` or ``float`` of standard deviation, depending on
        the self.decimal_precision
        """
        load_times = []
        # Handle edge cases like TTFB
        if asset_type == 'ttfb':
            for page in self.pages:
                load_times.append(page.time_to_first_byte)
        elif asset_type not in self.asset_types and asset_type != 'page':
            raise ValueError('asset_type must be one of:\nttfb\n{0}'.format(
                '\n'.join(self.asset_types)))
        else:
            load_times = self.get_load_times(asset_type)

        return round(numpy.std(load_times, ddof=1),
                     self.decimal_precision)

    @property
    def pages(self):
        """
        The aggregate pages of all the parser objects.
        """
        pages = []
        for har_dict in self.har_data:
            har_parser = HarParser(har_data=har_dict)
            if self.page_id:
                for page in har_parser.pages:
                    if page.page_id == self.page_id:
                        pages.append(page)
            else:
                pages.append(har_parser.pages[0])
        return pages

    @cached_property
    def asset_types(self):
        """
        Mimic the asset types stored in HarPage
        """
        return self.pages[0].asset_types

    @cached_property
    def time_to_first_byte(self):
        """
        The aggregate time to first byte for all pages.
        """
        ttfb = []
        for page in self.pages:
            ttfb.append(page.time_to_first_byte)
        return round(numpy.mean(ttfb), self.decimal_precision)

    @cached_property
    def page_load_time(self):
        """
        The average total load time for all runs (not weighted).
        """
        load_times = self.get_load_times('page')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    def js_load_time(self):
        """
        Returns aggregate javascript load time.

        :param total: ``bool`` indicating whether this should be should be the
        total load time or the browser load time
        """
        load_times = self.get_load_times('js')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    def css_load_time(self):
        """
        Returns aggregate css load time for all pages.
        """
        load_times = self.get_load_times('css')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    def image_load_time(self):
        """
        Returns aggregate image load time for all pages.
        """
        load_times = self.get_load_times('image')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    def html_load_time(self):
        """
        Returns aggregate html load time for all pages.
        """
        load_times = self.get_load_times('html')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    def audio_load_time(self):
        """
        Returns aggregate audio load time for all pages.
        """
        load_times = self.get_load_times('audio')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    def video_load_time(self):
        """
        Returns aggregate video load time for all pages.
        """
        load_times = self.get_load_times('video')
        return round(numpy.mean(load_times), self.decimal_precision)


class HarPage(object):
    """
    An object representing one page of a HAR resource
    """

    def __init__(self, page_id, har_parser=None, har_data=None):
        """
        :param page_id: ``str`` of the page ID
        :param parser: a HarParser object
        :param har_data: ``dict`` of a file HAR file
        """
        self.page_id = page_id
        if har_parser is None and har_data is None:
            raise ValueError('Either parser or har_data is required')
        if har_parser:
            self.parser = har_parser
        else:
            self.parser = HarParser(har_data=har_data)

        # This maps the content type attributes to their respective regex
        # representations
        self.asset_types = {'image': 'image.*',
                            'css': '.*css',
                            'text': 'text.*',
                            'js': '.*javascript',
                            'audio': 'audio.*',
                            'video': 'video.*|.*flash',
                            'html': 'html',
                            }

        # Init properties that mimic the actual 'pages' object from the HAR file
        raw_data = self.parser.har_data
        for page in raw_data['pages']:
            if page['id'] == self.page_id:
                self.title = page['title']
                self.startedDateTime = page['startedDateTime']
                self.pageTimings = page['pageTimings']

    def _get_asset_files(self, asset_type):
        """
        Returns a list of all files of a certain type.
        """
        return self.filter_entries(content_type=self.asset_types[asset_type])

    def _get_asset_size(self, asset_type):
        """
        Helper function to dynamically create *_size properties.
        """
        if asset_type == 'page':
            assets = self.entries
        else:
            assets = getattr(self, '{0}_files'.format(asset_type), None)
        return self.get_total_size(assets)

    def _get_asset_load(self, asset_type):
        """
        Helper function to dynamically create *_load_time properties. Return
        value is in ms.
        """
        if asset_type == 'initial':
            return self.actual_page['time']
        elif asset_type == 'content':
            return self.pageTimings['onContentLoad']
        elif asset_type == 'page':
            return self.pageTimings['onLoad']
        else:
            return self.get_load_time(content_type=self.asset_types[asset_type])

    def filter_entries(self, request_type=None, content_type=None,
                       status_code=None, regex=True):
        """
        Returns a ``list`` of entry objects based on the filter criteria.

        :param request_type: ``str`` of request type (i.e. - GET or POST)
        :param content_type: ``str`` of regex to use for finding content type
        :param status_code: ``int`` of the desired status code
        :param regex: ``bool`` indicating whether to use regex or exact match.
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
            p = self.parser
            if request_type is not None and not p.match_request_type(
                    entry, request_type, regex=regex):
                valid_entry = False
            if content_type is not None and not p.match_headers(
                    entry, 'response', 'Content-Type', content_type,
                    regex=regex):
                valid_entry = False
            if status_code is not None and not p.match_status_code(
                    entry, status_code, regex=regex):
                valid_entry = False

            if valid_entry:
                results.append(entry)

        return results

    def get_load_time(self, request_type=None, content_type=None,
                      status_code=None, async=True):
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

    def get_total_size(self, entries):
        """
        Returns the total size of a collection of entries.

        :param entries: ``list`` of entries to calculate the total size of.
        """
        size = 0
        for entry in entries:
            if entry['response']['bodySize'] > 0:
                size += entry['response']['bodySize']
        return size

    # BEGIN PROPERTIES #

    @cached_property
    def hostname(self):
        """
        Hostname of the initial request
        """
        for header in self.entries[0]['request']['headers']:
            if header['name'] == 'Host':
                return header['value']

    @cached_property
    def url(self):
        """
        The absolute URL of the initial request.
        """
        return self.entries[0]['request']['url']

    @cached_property
    def entries(self):
        page_entries = []
        for entry in self.parser.har_data['entries']:
            if entry['pageref'] == self.page_id:
                page_entries.append(entry)
        # Make sure the entries are sorted chronologically
        return sorted(page_entries,
                      key=lambda entry: entry['startedDateTime'])

    @cached_property
    def time_to_first_byte(self):
        """
        Time to first byte of the page request in ms
        """
        initial_entry = self.entries[0]
        ttfb = 0
        for k, v in iteritems(initial_entry['timings']):
            if k != 'receive':
                ttfb += v
        return ttfb

    @cached_property
    def get_requests(self):
        """
        Returns a list of GET requests, each of which is an 'entry' data object
        """
        return self.filter_entries(request_type='get')

    @cached_property
    def post_requests(self):
        """
        Returns a list of POST requests, each of which is an 'entry' data object
        """
        return self.filter_entries(request_type='post')

    # FILE TYPE PROPERTIES #

    @cached_property
    def actual_page(self):
        """
        Returns the first entry object that does not have a redirect status,
        indicating that it is the actual page we care about (after redirects).
        """
        for entry in self.entries:
            if not (entry['response']['status'] >= 300 and
                    entry['response']['status'] <= 399):
                return entry

    # Convenience properties. Easy accessible through the API, but even easier
    # to use as properties
    @cached_property
    def image_files(self):
        return self._get_asset_files('image')

    @cached_property
    def css_files(self):
        return self._get_asset_files('css')

    @cached_property
    def text_files(self):
        return self._get_asset_files('text')

    @cached_property
    def js_files(self):
        return self._get_asset_files('js')

    @cached_property
    def audio_files(self):
        return self._get_asset_files('audio')

    @cached_property
    def video_files(self):
        return self._get_asset_files('video')

    @cached_property
    def html_files(self):
        return self._get_asset_files('html')

    @cached_property
    def page_size(self):
        return self._get_asset_size('page')

    @cached_property
    def image_size(self):
        return self._get_asset_size('image')

    @cached_property
    def css_size(self):
        return self._get_asset_size('css')

    @cached_property
    def text_size(self):
        return self._get_asset_size('text')

    @cached_property
    def js_size(self):
        return self._get_asset_size('js')

    @cached_property
    def audio_size(self):
        return self._get_asset_size('audio')

    @cached_property
    def video_size(self):
        return self._get_asset_size('video')

    @cached_property
    def initial_load_time(self):
        return self._get_asset_load('initial')

    @cached_property
    def content_load_time(self):
        return self._get_asset_load('content')

    @cached_property
    def page_load_time(self):
        return self._get_asset_load('page')

    @cached_property
    def image_load_time(self):
        return self._get_asset_load('image')

    @cached_property
    def css_load_time(self):
        return self._get_asset_load('css')

    @cached_property
    def js_load_time(self):
        return self._get_asset_load('js')

    @cached_property
    def audio_load_time(self):
        return self._get_asset_load('audio')

    @cached_property
    def video_load_time(self):
        return self._get_asset_load('video')

    @cached_property
    def html_load_time(self):
        return self._get_asset_load('html')
