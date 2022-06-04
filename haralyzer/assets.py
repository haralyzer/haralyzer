# pylint: disable=C0302
"""
Provides all the main functional classes for analyzing HAR files
"""

import functools
import datetime
import json
import re
from typing import List, Optional

from collections import Counter
from cached_property import cached_property

# I know this import is stupid, but I cannot use dateutil.parser without it
from dateutil import parser

from .errors import PageNotFoundError
from .http import Request, Response
from .mixins import MimicDict

DECIMAL_PRECISION = 0


def convert_to_entry(func):
    """Wrapper function for converting dicts of entries to HarEnrty Objects"""

    @functools.wraps(func)
    def inner(*args, **kwargs):
        # Changed to list because tuple does not support item assignment
        changed_args = list(args)
        # Convert the dict (first argument) to HarEntry
        if isinstance(changed_args[0], dict):
            changed_args[0] = HarEntry(changed_args[0])
        return func(*tuple(changed_args), **kwargs)

    return inner


class HarParser:
    """
    A Basic HAR parser that also adds helpful stuff for analyzing the
    performance of a web page.
    """

    def __init__(self, har_data: dict = None):
        """
        :param har_data: a ``dict`` representing the JSON of a HAR file
        (i.e. - you need to load the HAR data into a string using json.loads or
        requests.json() if you are pulling the data via HTTP.
        """
        if not har_data or not isinstance(har_data, dict):
            raise ValueError(
                "A dict() representation of a HAR file is required"
                " to instantiate this class. Please RTFM."
            )
        self.har_data = har_data["log"]

    @staticmethod
    def from_file(file: [str, bytes]) -> 'HarParser':
        """
        Function create a HarParser from a file path

        :param file: Path to har file or bytes of har file
        :type file: [str, bytes]
        :return: HarParser Object
        :rtype HarParser
        """
        with open(file=file, mode="r", encoding="utf-8") as infile:
            return HarParser(json.load(infile))

    @staticmethod
    def from_string(data: [str, bytes]):
        """
        Function to load string or bytes as a HarParser

        :param data: Input string or bytes
        :type  data: [str, bytes]
        :return: HarParser Object
        :rtype HarParser
        """
        return HarParser(json.loads(data))

    @staticmethod
    @convert_to_entry
    def match_headers(
        entry: "HarEntry", header_type: str, header: str, value: str, regex: bool = True
    ) -> bool:
        # pylint: disable=R0913
        """
        Function to match headers.

        Since the output of headers might use different case, like:

            'content-type' vs 'Content-Type'

        This function is case-insensitive

        :param entry: Entry to analyze
        :type entry: HarEntry
        :param header_type: Header type. Valid values: 'request', or 'response'
        :type header_type: str
        :param header: The header to search for
        :type header: str
        :param value: The value to search for
        :type value: str
        :param regex: Whether to use regex or exact match
        :type regex: bool

        :returns: Whether a match was found
        :rtype: bool
        """
        if header_type not in ["request", "response"]:
            raise ValueError(
                "Invalid header_type, should be either:\n\n" "* 'request'\n*'response'"
            )

        # TODO - headers are empty in some HAR data.... need fallbacks here
        for h in getattr(entry, header_type).headers:
            if h["name"].lower() == header.lower() and h["value"] is not None:
                if regex and re.search(value, h["value"], flags=re.IGNORECASE):
                    return True
                if value == h["value"]:
                    return True
        return False

    @staticmethod
    @convert_to_entry
    def match_content_type(
        entry: "HarEntry", content_type: str, regex: bool = True
    ) -> bool:
        """
        Matches the content type of a request using the mimeType metadata.

        :param entry: Entry to analyze
        :type entry: HarEntry
        :param content_type: Regex to use for finding content type
        :type content_type: str
        :param regex: Whether to use regex or exact match.
        :type regex: bool
        :return: Mime type matches
        :rtype: bool
        """
        mime_type = entry.response.mimeType

        if regex and re.search(content_type, mime_type, flags=re.IGNORECASE):
            return True
        if content_type == mime_type:
            return True

        return False

    @staticmethod
    @convert_to_entry
    def match_request_type(
        entry: "HarEntry", request_type: str, regex: bool = True
    ) -> bool:
        """
        Helper function that returns entries with a request type
        matching the given `request_type` argument.

        :param entry: Entry to analyze
        :type entry: HarEntry
        :param request_type: Request type to match
        :type request_type: str
        :param regex: Whether to use a regex or string match
        :type regex: bool
        :return: Request method matches
        :rtype: bool
        """
        if regex:
            return (
                re.search(request_type, entry.request.method, flags=re.IGNORECASE)
                is not None
            )
        return entry.request.method == request_type

    @staticmethod
    @convert_to_entry
    def match_http_version(
        entry: "HarEntry", http_version: str, regex: bool = True
    ) -> bool:
        """
        Helper function that returns entries with a request type
        matching the given `request_type` argument.

        :param entry: Entry to analyze
        :type entry: HarEntry
        :param http_version: HTTP version type to match
        :type http_version: str
        :param regex: Whether to use a regex or string match
        :type regex: bool
        :return: HTTP version matches
        :rtype: bool
        """
        response_version = entry.response.httpVersion
        if regex:
            return (
                re.search(http_version, response_version, flags=re.IGNORECASE)
                is not None
            )
        return response_version == http_version

    @staticmethod
    @convert_to_entry
    def match_status_code(
        entry: "HarEntry", status_code: str, regex: bool = True
    ) -> bool:
        """
        Helper function that returns entries with a status code matching
        then given `status_code` argument.

        NOTE: This is doing a STRING comparison NOT NUMERICAL

        :param entry: Entry to analyze
        :type entry: HarEntry
        :param status_code: Status code to search for
        :type status_code: str
        :param regex: Whether to use a regex or string match
        :type regex: bool
        :return: Status code matches
        :rtype: bool
        """
        if regex:
            return re.search(status_code, str(entry.response.status)) is not None
        return str(entry.response.status) == status_code

    @staticmethod
    def create_asset_timeline(asset_list: List["HarEntry"]) -> dict:
        """
        Returns a `dict` of the timeline for the requested assets. The key is
        a datetime object (down to the millisecond) of ANY time where at least
        one of the requested assets was loaded. The value is a `list` of ALL
        assets that were loading at that time.

        :param asset_list: The assets to create a timeline for.
        :type asset_list: List[HarEntry]
        :return: Milliseconds and assets that were loaded
        :rtype: dict
        """
        results = {}
        for asset in asset_list:
            time_key = asset.startTime
            load_time = int(asset.time)
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
    def pages(self) -> List["HarPage"]:
        """
        This is a list of HarPage objects, each of which represents a page
        from the HAR file.

        :return: HarPages in the file
        :rtype: List[HarPage]
        """
        # Start with a page object for unknown entries if the HAR data has
        # any entries with no page ID
        pages = []
        if any("pageref" not in entry for entry in self.har_data["entries"]):
            pages.append(HarPage("unknown", har_parser=self))
        for har_page in self.har_data["pages"]:
            page = HarPage(har_page["id"], har_parser=self)
            pages.append(page)

        return pages

    @property
    def browser(self) -> str:
        """
        Browser of Har File

        :return: Browser of the Har File
        :rtype: str
        """
        return self.har_data["browser"]

    @property
    def version(self) -> str:
        """
        HAR Version

        :return: Version of HAR used
        :rtype: str
        """
        return self.har_data["version"]

    @property
    def creator(self) -> str:
        """
        Creator of Har File. Usually the same as the browser but not always

        :return: Program that created the HarFile
        :rtype: str
        """
        return self.har_data["creator"]

    @cached_property
    def hostname(self) -> str:
        """
        Hostname of first page

        :return: Hostname of the first known page
        :rtype: str
        """
        valid_pages = [p for p in self.pages if p.page_id != "unknown"]
        return valid_pages[0].hostname


class HarPage:
    # pylint: disable=R0904
    """
    An object representing one page of a HAR resource
    """

    def __init__(
        self, page_id: str, har_parser: "HarParser" = None, har_data: dict = None
    ):
        """
        :param page_id: Page ID
        :type page_id: str
        :param har_parser: HarParser object
        :type har_parser: HarParser
        :param har_data: HAR file
        :type har_data: dict
        """
        self.page_id = page_id
        self._index = 0
        if har_parser is None and har_data is None:
            raise ValueError("Either parser or har_data is required")
        if har_parser:
            self.parser = har_parser
        else:
            self.parser = HarParser(har_data=har_data)

        # This maps the content type attributes to their respective regex
        # representations
        self.asset_types = {
            "image": "image.*",
            "css": ".*css",
            "text": "text.*",
            "js": ".*javascript",
            "audio": "audio.*",
            "video": "video.*|.*flash",
            "html": "html",
        }

        # Init properties that mimic the actual 'pages' object from the HAR file
        raw_data = self.parser.har_data
        valid = False
        if self.page_id == "unknown":
            valid = True
        for page in raw_data["pages"]:
            if page["id"] == self.page_id:
                valid = True
                self.title = page.get("title", "")
                self.startedDateTime = page["startedDateTime"]
                self.pageTimings = page["pageTimings"]

        if not valid:
            page_ids = [page["id"] for page in raw_data["pages"]]
            raise PageNotFoundError(
                f"No page found with id {self.page_id}\n\nPage ID's are {page_ids}"
            )

    def __repr__(self):
        return f"ID: {self.page_id}, URL: {self.url}"

    def __iter__(self):
        return iter(self.entries)

    def __next__(self):
        # pylint: disable=W0707
        try:
            result = self.entries[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return result

    def _get_asset_files(self, asset_type: str) -> List["HarEntry"]:
        """
        Returns a list of all HarEntry object of a certain file type.
        :param asset_type: Asset type to filter for
        :type asset_type: str
        :return: List of HarEntry objects that meet the
        :rtype: List[HarEntry]
        """
        return self.filter_entries(content_type=self.asset_types[asset_type])

    def _get_asset_size_trans(self, asset_type: str) -> int:
        """
        Helper function to dynamically create *_size properties.
        :param asset_type: Asset type to filter for
        :type asset_type: str
        :return: Size of transferred data
        :rtype: int
        """
        if asset_type == "page":
            assets = self.entries
        else:
            assets = getattr(self, f"{asset_type}_files", None)
        return self.get_total_size_trans(assets)

    def _get_asset_size(self, asset_type: str):
        """
        Helper function to dynamically create *_size properties.
        :param asset_type: Asset type to filter for
        :type asset_type: str
        :return: Size of assets
        :rtype: int
        """
        if asset_type == "page":
            assets = self.entries
        else:
            assets = getattr(self, f"{asset_type}_files", None)
        return self.get_total_size(assets)

    def _get_asset_load(self, asset_type: str) -> Optional[int]:
        """
        Helper function to dynamically create *_load_time properties. Return
        value is in ms.
        :param asset_type: Asset type to filter for
        :type asset_type: str
        :return: Time of loading asset
        :rtype: int
        """
        if asset_type == "initial":
            return self.actual_page.time
        if asset_type == "content":
            return self.pageTimings["onContentLoad"]
        if asset_type == "page":
            if self.page_id == "unknown":
                return None
            return self.pageTimings["onLoad"]
            # TODO - should we return a slightly fake total load time to
            # accommodate HAR data that cannot understand things like JS
            # rendering or just throw a warning?
            # return self.get_load_time(
            #   request_type='.*',
            #   content_type='.*',
            #   status_code='.*',
            #   asynchronous=False)
        return self.get_load_time(content_type=self.asset_types[asset_type])

    def filter_entries(
        self,
        request_type: str = None,
        content_type: str = None,
        status_code: str = None,
        http_version: str = None,
        load_time__gt: int = None,
        regex: bool = True,
    ) -> List["HarEntry"]:
        # pylint: disable=R0913,W0105
        """
        Generate a list of entries with from criteria

        :param request_type: The request type (i.e. - GET or POST)
        :type request_type: str
        :param content_type: Regex to use for finding content type
        :type content_type: str
        :param status_code: The desired status code
        :type status_code: str
        :param http_version: HTTP version of request
        :type http_version: str
        :param load_time__gt: Load time in milliseconds. If
            provided, an entry whose load time is less than this value will
            be excluded from the results.
        :type load_time__gt: int
        :param regex: Whether to use regex or exact match.
        :type regex: bool
        :return: List of entry objects based on the filtered criteria.
        :rtype: List[HarEntry]
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
                entry, request_type, regex=regex
            ):
                valid_entry = False
            if content_type is not None:
                if not self.parser.match_content_type(entry, content_type, regex=regex):
                    valid_entry = False
            if status_code is not None and not p.match_status_code(
                entry, status_code, regex=regex
            ):
                valid_entry = False
            if http_version is not None and not p.match_http_version(
                entry, http_version, regex=regex
            ):
                valid_entry = False
            if load_time__gt is not None and entry.time < load_time__gt:
                valid_entry = False

            if valid_entry:
                results.append(entry)

        return results

    def get_load_time(
        self,
        request_type: str = None,
        content_type: str = None,
        status_code: str = None,
        asynchronous: bool = True,
        **kwargs,
    ) -> int:
        """
        This method can return the TOTAL load time for the assets or the ACTUAL
        load time, the difference being that the actual load time takes
        asynchronous transactions into account. So, if you want the total load
        time, set asynchronous=False.

        EXAMPLE:

        I want to know the load time for images on a page that has two images,
        each of which took 2 seconds to download, but the browser downloaded
        them at the same time.

        self.get_load_time(content_types=['image']) (returns 2)
        self.get_load_time(content_types=['image'], asynchronous=False) (returns 4)

        :param request_type: The request type (i.e. - GET or POST)
        :type request_type: str
        :param content_type: Regex to use for finding content type
        :type content_type: str
        :param status_code: The desired status code
        :type status_code: str
        :param asynchronous: Whether to separate load times
        :type asynchronous: bool
        :return: Total load time
        :rtype: int
        """
        entries = self.filter_entries(
            request_type=request_type,
            content_type=content_type,
            status_code=status_code,
        )

        asynchronous = kwargs.get("async", asynchronous)

        if not asynchronous:
            time = 0
            for entry in entries:
                time += entry.time
            return time
        return len(self.parser.create_asset_timeline(entries))

    @staticmethod
    def get_total_size(entries: List["HarEntry"]) -> int:
        """
        Returns the total size of a collection of entries.

        :param entries: ``list`` of entries to calculate the total size of.
        :return: Total size of entries
        :rtype: int
        """
        size = 0
        for entry in entries:
            if entry.response.bodySize > 0:
                size += entry.response.bodySize
        return size

    @staticmethod
    def get_total_size_trans(entries: List["HarEntry"]) -> int:
        """
        Returns the total size of a collection of entries - transferred.

        NOTE: use with har file generated with chrome-har-capturer

        :param entries: ``list`` of entries to calculate the total size of.
        :return: Total size of entries that was transferred
        :rtype: int
        """
        size = 0
        for entry in entries:
            if entry.response.raw_entry["_transferSize"] > 0:
                size += entry.response.raw_entry["_transferSize"]
        return size

    # BEGIN PROPERTIES #

    @cached_property
    def hostname(self) -> str:  # pylint: disable=R1710
        """
        :return: Hostname of the initial request
        :rtype: str
        """
        for header in self.entries[0].request.headers:
            if header["name"] == "Host":
                return header["value"]

    @cached_property
    def url(self) -> Optional[str]:
        """
        The absolute URL of the initial request.

        :return: URL of first request
        :rtype: str
        """
        if (
            "request" in self.entries[0].raw_entry
            and "url" in self.entries[0].request.raw_entry
        ):
            return self.entries[0].request.url
        return None

    @cached_property
    def entries(self) -> List["HarEntry"]:
        """
        :return: All entries that make up the page
        :rtype: List[HarEntry]
        """
        page_entries = []
        for entry in self.parser.har_data["entries"]:
            if "pageref" not in entry:
                if self.page_id == "unknown":
                    page_entries.append(HarEntry(entry))
            elif entry["pageref"] == self.page_id:
                page_entries.append(HarEntry(entry))
        # Make sure the entries are sorted chronologically
        if all(x.startTime for x in page_entries):
            return sorted(page_entries, key=lambda entry: entry.startTime)
        return page_entries

    @cached_property
    def time_to_first_byte(self) -> Optional[int]:
        """
        :return: Time to first byte of the page request in ms
        :rtype: int
        """
        # The unknown page is just a placeholder for entries with no page ID.
        # As such, it would not have a TTFB
        if self.page_id == "unknown":
            return None
        ttfb = 0
        for entry in self.entries:
            if entry.response.status == 200:
                for k, v in entry.timings.items():
                    if k != "receive":
                        if v > 0:
                            ttfb += v
                break
            ttfb += entry.time

        return ttfb

    @cached_property
    def get_requests(self) -> List["HarEntry"]:
        """
        Returns a list of GET requests, each of which is a HarEntry object

        :return: All GET requests
        :rtype: List[HarEntry]
        """
        return self.filter_entries(request_type="get")

    @cached_property
    def post_requests(self) -> List["HarEntry"]:
        """
        Returns a list of POST requests, each of which is an HarEntry object

        :return: All POST requests
        :rtype: List[HarEntry]
        """
        return self.filter_entries(request_type="post")

    # FILE TYPE PROPERTIES #

    @cached_property
    def actual_page(self) -> "HarEntry":  # pylint: disable=R1710
        """
        Returns the first entry object that does not have a redirect status,
        indicating that it is the actual page we care about (after redirects).

        :return: First entry of the page
        :rtype: HarEntry
        """
        for entry in self.entries:
            if not 300 <= entry.response.status <= 399:
                return entry

    @cached_property
    def duplicate_url_request(self) -> dict:
        """
        Returns a dict of urls and its number of repetitions that are sent more than once

        :return: URLs and the amount of times they were duplicated
        :rtype: dict
        """
        counted_urls = Counter([entry.request.url for entry in self.entries])
        return {k: v for k, v in counted_urls.items() if v > 1}

    # Convenience properties. Easy accessible through the API, but even easier
    # to use as properties
    @cached_property
    def image_files(self) -> List["HarEntry"]:
        """
        All image files for a page

        :return: Image entries for a page
        :rtype: List[HarEntry]
        """
        return self._get_asset_files("image")

    @cached_property
    def css_files(self) -> List["HarEntry"]:
        """
        All CSS files for a page

        :return: CSS entries for a page
        :rtype: List[HarEntry]
        """
        return self._get_asset_files("css")

    @cached_property
    def text_files(self) -> List["HarEntry"]:
        """
        All text files for a page

        :return: Text entries for a page
        :rtype: List[HarEntry]
        """
        return self._get_asset_files("text")

    @cached_property
    def js_files(self) -> List["HarEntry"]:
        """
        All JS files for a page

        :return: JS entries for a page
        :rtype: List[HarEntry]
        """
        return self._get_asset_files("js")

    @cached_property
    def audio_files(self) -> List["HarEntry"]:
        """
        All audio files for a page

        :return: Audio entries for a page
        :rtype: List[HarEntry]
        """
        return self._get_asset_files("audio")

    @cached_property
    def video_files(self) -> List["HarEntry"]:
        """
        All video files for a page

        :return: Video entries for a page
        :rtype: List[HarEntry]
        """
        return self._get_asset_files("video")

    @cached_property
    def html_files(self) -> List["HarEntry"]:
        """
        All HTML files for a page

        :return: HTML entries for a page
        :rtype: List[HarEntry]
        """
        return self._get_asset_files("html")

    @cached_property
    def page_size(self) -> int:
        """
        Size of the page

        :return: Size of the page
        :rtype: int
        """
        return self._get_asset_size("page")

    @cached_property
    def image_size(self) -> int:
        """
        Size of image files from the page

        :return: Size of image files on the page
        :rtype: int
        """
        return self._get_asset_size("image")

    @cached_property
    def css_size(self) -> int:
        """
        Size of CSS files from the page

        :return: Size of CSS files on the page
        :rtype: int
        """
        return self._get_asset_size("css")

    @cached_property
    def text_size(self) -> int:
        """
        Size of text files from the page

        :return: Size of text files on the page
        :rtype: int
        """
        return self._get_asset_size("text")

    @cached_property
    def js_size(self) -> int:
        """
        Size of JS files from the page

        :return: Size of JS files on the page
        :rtype: int
        """
        return self._get_asset_size("js")

    @cached_property
    def audio_size(self) -> int:
        """
        Size of audio files from the page

        :return: Size of audio files on the page
        :rtype: int
        """
        return self._get_asset_size("audio")

    @cached_property
    def video_size(self) -> int:
        """
        Size of video files from the page

        :return: Size of video files on the page
        :rtype: int
        """
        return self._get_asset_size("video")

    @cached_property
    def page_size_trans(self) -> int:
        """
        Page transfer size

        :return: Size of transfer data for the page
        :rtype: int
        """
        return self._get_asset_size_trans("page")

    @cached_property
    def image_size_trans(self) -> int:
        """
        Image transfer size

        :return: Size of transfer data for images
        :rtype: int
        """
        return self._get_asset_size_trans("image")

    @cached_property
    def css_size_trans(self) -> int:
        """
        CSS transfer size

        :return: Size of transfer data for CSS
        :rtype: int
        """
        return self._get_asset_size_trans("css")

    @cached_property
    def text_size_trans(self) -> int:
        """
        Text transfer size

        :return: Size of transfer data for text
        :rtype: int
        """
        return self._get_asset_size_trans("text")

    @cached_property
    def js_size_trans(self) -> int:
        """
        JS transfer size

        :return: Size of transfer data for JS
        :rtype: int
        """
        return self._get_asset_size_trans("js")

    @cached_property
    def audio_size_trans(self) -> int:
        """
        Audio transfer size

        :return: Size of transfer data for audio
        :rtype: int
        """
        return self._get_asset_size_trans("audio")

    @cached_property
    def video_size_trans(self) -> int:
        """
        Video transfer size

        :return: Size of transfer data for images
        :rtype: int
        """
        return self._get_asset_size_trans("video")

    @cached_property
    def initial_load_time(self) -> int:
        """
        Initial load time

        :return: Initial load time of the page
        :rtype: int
        """
        return self._get_asset_load("initial")

    @cached_property
    def content_load_time(self) -> int:
        """
        Content load time

        :return: Load time for all content
        :rtype: int
        """
        return self._get_asset_load("content")

    @cached_property
    def page_load_time(self) -> int:
        """
        Load time of the page

        :return: Load time for the page
        :rtype: int
        """
        return self._get_asset_load("page")

    @cached_property
    def image_load_time(self) -> int:
        """
        Image load time

        :return: Load time for images on a page
        :rtype: int
        """
        return self._get_asset_load("image")

    @cached_property
    def css_load_time(self) -> int:
        """
        CSS load time

        :return: Load time for CSS on a page
        :rtype: int
        """
        return self._get_asset_load("css")

    @cached_property
    def js_load_time(self) -> int:
        """
        JS load time

        :return: Load time for JS on a page
        :rtype: int
        """
        return self._get_asset_load("js")

    @cached_property
    def audio_load_time(self) -> int:
        """
        Audio load time

        :return: Load time for audio on a page
        :rtype: int
        """
        return self._get_asset_load("audio")

    @cached_property
    def video_load_time(self) -> int:
        """
        Video load time

        :return: Load time for video on a page
        :rtype: int
        """
        return self._get_asset_load("video")

    @cached_property
    def html_load_time(self) -> int:
        """
        HTML load time

        :return: Load time for HTML on a page
        :rtype: int
        """
        return self._get_asset_load("html")


class HarEntry(MimicDict):
    """
    An object that represent one entry in a HAR Page
    """

    def __init__(self, entry: dict):
        self.raw_entry = entry
        super().__init__()

    def __str__(self):
        return f"HarEntry for {self.url}"

    def __repr__(self):
        return f"HarEntry for {self.url}"

    @cached_property
    def request(self) -> Request:
        """
        :return: Request of the entry
        :rtype: Request
        """
        return Request(entry=self.raw_entry["request"])

    @cached_property
    def response(self) -> Response:
        """
        :return: Response of the entry
        :rtype: Response
        """
        return Response(url=self.url, entry=self.raw_entry["response"])

    @cached_property
    def startTime(self) -> Optional[datetime.datetime]:
        # pylint: disable=W0212
        """
        Start time and date

        :return: Start time of entry
        :rtype: Optional[datetime.datetime]
        """
        try:
            return parser.parse(self.raw_entry.get("startedDateTime", ""))
        except parser._parser.ParserError:
            return None

    @cached_property
    def cache(self) -> str:
        """
        :return: Cached objects
        :rtype: str
        """
        return self.raw_entry["cache"]

    @cached_property
    def cookies(self) -> list:
        """
        :return: Request and Response Cookies
        :rtype: list
        """
        return self.raw_entry.get("cookies", [])

    @cached_property
    def pageref(self) -> str:
        """
        :return: Page for the entry
        :rtype: str
        """
        return self.raw_entry["pageref"]

    @cached_property
    def port(self) -> int:
        """
        :return: Port connection was made to
        :rtype: int
        """
        return int(self.raw_entry["connection"])

    @cached_property
    def secure(self) -> bool:
        """
        :return: Connection was secure
        :rtype: bool
        """
        return self.raw_entry.get("_securityState", "") == "secure"

    @cached_property
    def serverAddress(self) -> str:
        """
        :return: IP Address of the server
        :rtype: str
        """
        return self.raw_entry["serverIPAddress"]

    @cached_property
    def status(self) -> int:
        """
        :return: HTTP Status Code
        :rtype: int
        """
        return self.raw_entry["response"]["status"]

    @cached_property
    def time(self) -> int:
        """
        :return: Time taken to complete entry
        :rtype: int
        """
        return self.raw_entry["time"]

    @cached_property
    def timings(self) -> dict:
        """
        :return: Timing of the page load
        :rtype: dict
        """
        return self.raw_entry["timings"]

    @cached_property
    def url(self) -> str:
        """
        :return: URL of Entry
        :rtype: str"""
        return self.raw_entry["request"]["url"]
