"""
Provides all of the main functional classes for analyzing HAR files
"""

import datetime
import dateutil
# I know this import is stupid, but I cannot use dateutil.parser without it
from dateutil import parser
assert parser
import re


class HarParser(object):
    """
    A Basic HAR parser that also adds helpful stuff for analyzing the
    performance of a web page.
    """

    def __init__(self, har_data=None):
        """
        :param har: a ``dict`` representing the JSON of a HAR file (i.e. - you
        need to load the HAR data into a string using json.loads or
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

    def __getattr__(self, name):
        """
        Using some voodoo here to dynamically generate properties. This allows
        us to avoid defining tons of similar properties, like image_files,
        css_files, text_files, etc.). If the requested property should be
        created dynamically, but the asset type is not in
        self.asset_types a KeyError will be raised.
        """
        files_regex = '(\D.*)_files'
        size_regex = '(\D.*)_size'
        load_regex = '(\D.*)_load_time'
        # total_asset_load_time is no longer part of the API, but it used to
        # be, so this is in here for backwards compatability
        total_load_regex = 'total_(\D.*)_load_time'

        # Try to match the request to one of the regexes above.
        files_match = re.search(files_regex, name)
        size_match = re.search(size_regex, name)
        load_match = re.search(load_regex, name)
        total_load_match = re.search(total_load_regex, name)

        if files_match:
            asset_type = files_match.groups()[0]
            return self.filter_entries(
                content_type=self.asset_types[asset_type])

        elif size_match:
            asset_type = size_match.groups()[0]
            return self._get_asset_size(asset_type)

        elif load_match or total_load_match:
            match = total_load_match or load_match
            asset_type = match.groups()[0]
            return self._get_asset_load(asset_type)

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
        elif asset_type == 'total':
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
    def time_to_first_byte(self):
        """
        Time to first byte of the page request in ms
        """
        initial_entry = self.entries[0]
        ttfb = 0
        for k, v in initial_entry['timings'].iteritems():
            if k != 'receive':
                ttfb += v
        return ttfb

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

    # FILE TYPE PROPERTIES #

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
