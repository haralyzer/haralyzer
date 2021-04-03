"""Contains the mutlihar parse object"""
from statistics import stdev
from statistics import mean
from typing import Union, List
from cached_property import cached_property
from .assets import HarParser

DECIMAL_PRECISION = 0


class MultiHarParser:
    """
    An object that represents multiple HAR files OF THE SAME CONTENT.
    It is used to gather overall statistical data in situations where you have
    multiple runs against the same web asset, which is common in performance
    testing.
    """

    def __init__(self, har_data, page_id=None, decimal_precision=DECIMAL_PRECISION):
        """
        :param har_data: A list of dict representing the JSON
        of a HAR file. See the docstring of HarParser.__init__ for more detail.
        :type har_data: List[dict]
        :param page_id: IF a the page ID is provided, the
        multiparser will return aggregate results for this specific page. If
        not, it will assume that there is only one page in the run (this was
        written specifically for that use case).
        :type page_id: str
        :param decimal_precision: The precision of the.
        :type decimal_precision: int
        """
        self.har_data = har_data
        self.page_id = page_id
        self.decimal_precision = decimal_precision

    def get_load_times(self, asset_type: str) -> list:
        """
        Just a list of the load times of a certain asset type for each page

        :param asset_type: The asset type to return load times for
        :type asset_type: str
        :return: List of load times
        :rtype: list
        """
        load_times = []
        search_str = "{0}_load_time".format(asset_type)
        for har_page in self.pages:
            val = getattr(har_page, search_str, None)
            if val is not None:
                load_times.append(val)
        return load_times

    def get_stdev(self, asset_type: str) -> Union[int, float]:
        """
        Returns the standard deviation for a set of a certain asset type.

        :param asset_type: The asset type to calculate standard deviation for.
        :type asset_type: str
        :returns: Standard deviation, which can be an `int` or `float`
            depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = []
        # Handle edge cases like TTFB
        if asset_type == "ttfb":
            for page in self.pages:
                if page.time_to_first_byte is not None:
                    load_times.append(page.time_to_first_byte)
        elif asset_type not in self.asset_types and asset_type != "page":
            raise ValueError(
                "asset_type must be one of:\nttfb\n{0}".format(
                    "\n".join(self.asset_types)
                )
            )
        else:
            load_times = self.get_load_times(asset_type)

        if not load_times or not sum(load_times):
            return 0
        return round(stdev(load_times), self.decimal_precision)

    @property
    def pages(self) -> List["HarPage"]:  # noqa: F821
        """
        Aggregate pages of all the parser objects.

        :return: All the pages from parsers
        :rtype: List[haralyzer.assets.HarPage]
        """
        pages = []
        for har_dict in self.har_data:
            har_parser = HarParser(har_data=har_dict)
            if self.page_id:
                for page in har_parser.pages:
                    if page.page_id == self.page_id:
                        pages.append(page)
            else:
                pages = pages + har_parser.pages
        return pages

    @cached_property
    def asset_types(self) -> dict:
        """
        Mimic the asset types stored in HarPage

        :return: Asset types from HarPage
        :rtype: dict
        """
        return self.pages[0].asset_types

    @cached_property
    def time_to_first_byte(self) -> Union[int, float]:
        """
        :returns: The aggregate time to first byte for all pages.
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        ttfb = []
        for page in self.pages:
            if page.time_to_first_byte is not None:
                ttfb.append(page.time_to_first_byte)
        return round(mean(ttfb), self.decimal_precision)

    @cached_property
    def page_load_time(self) -> Union[int, float]:
        """
        :returns: Average total load time for all runs (not weighted).
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = self.get_load_times("page")
        return round(mean(load_times), self.decimal_precision)

    @cached_property
    def js_load_time(self) -> Union[int, float]:
        """
        :returns: Aggregate javascript load time.
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = self.get_load_times("js")
        return round(mean(load_times), self.decimal_precision)

    @cached_property
    def css_load_time(self) -> Union[int, float]:
        """
        :returns: Aggregate css load time for all pages.
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = self.get_load_times("css")
        return round(mean(load_times), self.decimal_precision)

    @cached_property
    def image_load_time(self) -> Union[int, float]:
        """
        :returns: Aggregate image load time for all pages.
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = self.get_load_times("image")
        return round(mean(load_times), self.decimal_precision)

    @cached_property
    def html_load_time(self) -> Union[int, float]:
        """
        :returns: Aggregate html load time for all pages.
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = self.get_load_times("html")
        return round(mean(load_times), self.decimal_precision)

    @cached_property
    def audio_load_time(self) -> Union[int, float]:
        """
        :returns: Aggregate audio load time for all pages.
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = self.get_load_times("audio")
        return round(mean(load_times), self.decimal_precision)

    @cached_property
    def video_load_time(self) -> Union[int, float]:
        """
        :returns: Aggregate video load time for all pages.
            Can be an `int` or `float` depending on the self.decimal_precision
        :rtype: int, float
        """
        load_times = self.get_load_times("video")
        return round(mean(load_times), self.decimal_precision)
