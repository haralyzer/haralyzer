class HarPage(object):

    def __init__(self, parser, page_id):
        """
        A Basic HAR parser that also adds helpful stuff for analyzing the
        performance of a web page.

        :param parser: a HarParser object
        :param page_id: ``str`` of the page ID
        """
        self.parser = parser
        self.page_id = page_id

    def filter_entries(self, request_type='', content_type='',
                       status_code='', regex=True):
        """
        Returns a ``list`` of entry objects based on the filter criteria.

        :param request_type: ``str`` of request type (i.e. - GET or POST)
        :param content_type: ``str`` of regex to use for finding content type
        :param status_code: ``int`` of the desired status code
        :param regex: ``bool`` indicating whether this should be a regex match
        or an exact string match
        """
        results = []
        request_type = request_type.upper()

        for entry in self.entries:
            """
            So yea... this is a bit ugly. We are looking for:

                * The request type using self._match_request_type()
                * The content type using self._match_headers()
                * The HTTP response status code using self._match_status_code()

            Oh lords of python.... please forgive my soul
            """
            if (self.parser.match_request_type(entry, request_type) and
                    self.parser.match_status_code(entry, status_code,
                                                  regex=regex) and
                    self.parser.match_headers(entry, 'request', 'Content-Type',
                                        regex=regex)):
                results.append(entry)

        return results

    def get_load_time(self, request_type='.*', content_type='.*',
                      status_code='.*', async=True):
        """
        Returns a ``dict`` of the timeline for the requested assets. The key is
        a datetime object (down to the millisecond) of ANY time where at least
        one of the requested assets was loaded. The value is a list of ALL
        assets that were loading at that time.

        This method can return the TOTAL load time for the assets or the ACTUAL
        load time, the difference being that the actual load time takes
        asyncronys transactions into account. So, if you want the total load
        time, set async=True.

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
            return len(self.parser._create_asset_timeline(entries))

    @property
    def entries(self):
        # Make sure the entries are sorted chronologically
        page_entries = []
        for entry in self.parser.har_data['entries']:
            if entry['pageref'] == self.page_id:
                page_entries.append(entry)
        return sorted(page_entries,
                      key=lambda asset: asset['startedDateTime'])

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
        Returns the total page size (in bytes) including all assets
        """
        size = 0
        for entry in self.entries:
            if entry['response']['bodySize'] and \
                    entry['response']['bodySize'] > 0:
                size += entry['response']['bodySize']
        return size

    @property
    def load_time(self):
        """
        Returns the full load time (in bytes) of the page itself
        """
        # Assuming for right now that the HAR file is only for one page
        return self.initial_page['time']

    @property
    def total_load_time(self):
        """
        Returns the full load time (in bytes) of all assets on the page
        """
        # Assuming for right now that the HAR file is only for one page
        return self.pages[0]['pageTimings']['onLoad']

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
