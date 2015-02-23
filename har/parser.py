import datetime
import dateutil
from dateutil import parser
assert parser

print 'test'
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
            raise ValueError('A dict() is required to instantiate this class.')
        self.har_data = har_data['log']

    def _match_headers(self, header, value):
        """
        Tiny little helper function to match headers.

        :param header: ``str`` of the header to search for
        :param value: ``str`` of a regex to search for in the header

        :returns: a ``list`` of all matching elements, each of which is an
        'entry' JSON object.
        """
        matches = []
        for entry in self.entries:
            for h in entry['response']['headers']:
                if h['name'] == header and h['value']:
                    if value in h['value']:
                        matches.append(entry)
        return matches

    def _create_asset_timeline(self, asset_type):
        """
        Super weird helper function that creates a data structure for analyzing
        the total load time of a certain type of asset. Since assets are loaded
        async, we cannot just add up the total time. This function creates a
        ``dict``. The keys are datetime objects representing a millisecond, and
        the values are a list of assets that were loading during that time. As
        such, for any given millisecond of the page load time, you can access
        a list to see what assets of the given type (and how many) were loading
        at that particlar time.

        :param asset_type: ``str`` of the asset type to search for
        """
        results = dict()
        asset_list = getattr(self, asset_type, None)
        # Return None if none of these assets were on the page
        if asset_list is None:
            return asset_list
        for asset in asset_list:
            time_key = dateutil.parser.parse(asset['startedDateTime'])
            load_time = asset['time']
            # Add the start time and asset to the results dict
            if time_key in results:
                results[time_key].append(asset)
            else:
                results[time_key] = [asset]
            # For each millisecond the asset was loading, insert the asset
            # into the appropriate key of the results dict
            for t in range(0, load_time):
                time_key = time_key + datetime.timedelta(milliseconds=1)
                if time_key in results:
                    results[time_key].append(asset)
                else:
                    results[time_key] = [asset]

        return results
    @property
    def pages(self):
        return self.har_data['pages']

    @property
    def browser(self):
        return self.har_data['browser']

    @property
    def entries(self):
        return self.har_data['entries']

    @property
    def version(self):
        return self.har_data['version']

    @property
    def creator(self):
        return self.har_data['creator']

    @property
    def get_requests(self):
        """
        Returns a list of GET requests, each of which is an 'entry' data object
        """
        return filter(lambda entry: entry['request']['method'] == 'GET',
                      self.entries)

    @property
    def post_requests(self):
        """
        Returns a list of POST requests, each of which is an 'entry' data object
        """
        return filter(lambda entry: entry['request']['method'] == 'POST',
                      self.entries)

    @property
    def images(self):
        """
        Returns a list of images, each of which is an 'entry' data object.
        """
        return self._match_headers('Content-Type', 'image')

    @property
    def css_files(self):
        """
        Returns a list of css files, each of which is an 'entry' data object.
        """
        return self._match_headers('Content-Type', 'css')

    @property
    def js_files(self):
        """
        Returns a list of javascript files, each of which is an 'entry'
        data object.
        """
        return self._match_headers('Content-Type', 'javascript')

    @property
    def initial_page(self):
        """
        Returns the first entry object that does not have a redirect status.
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
        return self.initial_page['response']['bodySize']

    @property
    def total_page_size(self):
        """
        Returns the total page size (in bytes) including all assets of the
        first non-redirect page
        """
        size = 0
        for entry in self.entries:
            if entry['response']['bodySize'] and \
                    entry['response']['bodySize'] != -1:
                size += entry['response']['bodySize']
        return size

    @property
    def load_time(self):
        """
        Returns the full load time (in bytes) of the page itself
        """
        # Assuming for right now that the HAR file is only for one page
        return self.pages[0]['pageTimings']['onContentLoad']

    @property
    def total_load_time(self):
        """
        Returns the full load time (in bytes) of all assets on the page
        """
        # Assuming for right now that the HAR file is only for one page
        return self.pages[0]['pageTimings']['onLoad']

    @property
    def image_load_time(self):
        """
        Returns the total load time for all images.
        """
        load_time = 0
        for entry in self.images:
            load_time += entry['time']
        return load_time

    @property
    def css_load_time(self):
        """
        Returns the total load time for all CSS files.
        """
        load_time = 0
        for entry in self.css_files:
            load_time += entry['time']
        return load_time

    @property
    def js_load_time(self):
        """
        Returns the total load time for all javascript files.
        """
        load_time = 0
        for entry in self.js_files:
            load_time += entry['time']
        return load_time
