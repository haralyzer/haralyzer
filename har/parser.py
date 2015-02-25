import datetime
import dateutil
from dateutil import parser
assert parser
import re
from .page import HarPage


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
            return re.search(entry['request']['method'],
                             request_type) is not None
        else:
            return entry['request']['method'] == request_type

    def match_status_code(self, entry, status_code, regex=True):
        """
        Helper function that returns request types based on the given regex

        :param entry: entry object to analyze
        :param request_type: ``regex`` of request type to match
        """
        if regex:
            return re.search(entry['response']['status'],
                             status_code) is not None
        else:
            return entry['response']['status'] == status_code

    def create_asset_timeline(self, asset_list):
        """
        Super weird helper function that creates a data structure for analyzing
        the total load time of a certain type of asset. Since assets are loaded
        async, we cannot just add up the total time. This function creates a
        ``dict``. The keys are datetime objects representing a millisecond, and
        the values are a list of assets that were loading during that time. As
        such, for any given millisecond of the page load time, you can access
        a list to see what assets (and more importantly, how many) were loading
        at that particlar time.

        :param asset_list: ``list`` of the assets to create a timeline for.
        """
        results = dict()
        # Return None if none of these assets were on the page
        if asset_list is None:
            return asset_list
        for asset in asset_list:
            time_key = dateutil.parser.parse(asset['startedDateTime'])
            load_time = int(asset['time'])
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
        pages = []
        for page_id in self.har_data['pages']:
            page = HarPage(self, page_id)
            pages.append(page)

    @property
    def browser(self):
        return self.har_data['browser']

    @property
    def version(self):
        return self.har_data['version']

    @property
    def creator(self):
        return self.har_data['creator']
