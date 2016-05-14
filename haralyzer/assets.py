"""
Provides all of the main functional classes for analyzing HAR files
"""

import datetime

import dateutil
from cached_property import cached_property

# I know this import is stupid, but I cannot use dateutil.parser without it
from dateutil import parser

assert parser
import re

from .compat import iteritems
from .errors import PageLoadTimeError, PageNotFoundError

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
            raise ValueError(
                'A dict() representation of a HAR file is required'
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

        # TODO - headers are empty in some HAR data.... need fallbacks here
        for h in entry[header_type]['headers']:
            if h['name'].lower() == header.lower() and h['value'] is not None:
                if regex and re.search(value, h['value'], flags=re.IGNORECASE):
                    return True
                elif value == h['value']:
                    return True
        return False

    @staticmethod
    def match_content_type(entry, content_type, regex=True):
        """
        Matches the content type of a request using the mimeType metadata.

        :param entry: ``dict`` of a single entry from a HarPage
        :param content_type: ``str`` of regex to use for finding content type
        :param regex: ``bool`` indicating whether to use regex or exact match.
        """
        mimeType = entry['response']['content']['mimeType']

        if regex and re.search(content_type, mimeType, flags=re.IGNORECASE):
            return True

        elif content_type == mimeType:
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

    @staticmethod
    def match_http_version(entry, http_version, regex=True):
        """
        Helper function that returns entries with a request type
        matching the given `request_type` argument.

        :param entry: entry object to analyze
        :param request_type: ``str`` of request type to match
        :param regex: ``bool`` indicating whether to use a regex or string match
        """
        response_version = entry['response']['httpVersion']
        if regex:
            return re.search(http_version, response_version,
                             flags=re.IGNORECASE) is not None
        else:
            return response_version == http_version

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
        valid = False
        for page in raw_data['pages']:
            if page['id'] == self.page_id:
                valid = True
                self.title = page['title']
                self.startedDateTime = page['startedDateTime']
                self.pageTimings = page['pageTimings']

        if not valid:
            page_ids = [page['id'] for page in raw_data['pages']]
            raise PageNotFoundError(
                    'No page found with id {0}\n\nPage ID\'s are {1}'.format(
                            self.page_id, page_ids)
            )

    def __repr__(self):
        return 'ID: {0}, URL: {1}'.format(self.page_id, self.url)

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
            if 'onLoad' in self.pageTimings:
                return self.pageTimings['onLoad']
            else:
                raise PageLoadTimeError('full page load time is not available')
            # TODO - should we return a slightly fake total load time to
            # accomodate HAR data that cannot understand things like JS
            # rendering or just throw a warning?
            #return self.get_load_time(request_type='.*',content_type='.*', status_code='.*', async=False)
        else:
            return self.get_load_time(
                content_type=self.asset_types[asset_type])

    def filter_entries(self, request_type=None, content_type=None,
                       status_code=None, http_version=None, regex=True):
        """
        Returns a ``list`` of entry objects based on the filter criteria.

        :param request_type: ``str`` of request type (i.e. - GET or POST)
        :param content_type: ``str`` of regex to use for finding content type
        :param status_code: ``int`` of the desired status code
        :param http_version: ``str`` of HTTP version of request
        :param regex: ``bool`` indicating whether to use regex or exact match.
        """
        results = []

        for entry in self.entries:
            """
            So yea... this is a bit ugly. We are looking for:

                * The request type using self._match_request_type()
                * The content type using self._match_headers()
                * The HTTP response status code using self._match_status_code()
                * The HTTP version using self._match_headers()

            Oh lords of python.... please forgive my soul
            """
            valid_entry = True
            p = self.parser
            if request_type is not None and not p.match_request_type(
                    entry, request_type, regex=regex):
                valid_entry = False
            if content_type is not None:
                if not self.parser.match_content_type(entry, content_type,
                                                      regex=regex):
                    valid_entry = False
            if status_code is not None and not p.match_status_code(
                    entry, status_code, regex=regex):
                valid_entry = False
            if http_version is not None and not p.match_http_version(
                    entry, http_version, regex=regex):
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

    def asset_load_time(self):
        """
        Total load time of all assets, including async loading. This is as
        close as you can get to the actual page load time if you have a HAR
        file that does not take browser side actions like javascript into
        account.
        """
        return len(self.parser.create_asset_timeline(self.entries))

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
