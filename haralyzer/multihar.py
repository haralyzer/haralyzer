from functools import wraps
import warnings

try:
    import numpy
except ImportError:
    has_numpy = False
else:
    has_numpy = True

from cached_property import cached_property

from .assets import HarParser

DECIMAL_PRECISION = 0


def needs_numpy(f):
    @wraps(f)
    def with_numpy(*args, **kwargs):
        if not has_numpy:
            warnings.warn("numpy is required to use this feature",
                          ImportWarning)
            return
        return f(*args, **kwargs)

    return with_numpy


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

        :param asset_type: ``str`` of the asset type to return load times for
        """
        load_times = []
        search_str = '{0}_load_time'.format(asset_type)
        for har_page in self.pages:
            val = getattr(har_page, search_str, None)
            load_times.append(val)
        return load_times

    @needs_numpy
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
    @needs_numpy
    def time_to_first_byte(self):
        """
        The aggregate time to first byte for all pages.
        """
        ttfb = []
        for page in self.pages:
            ttfb.append(page.time_to_first_byte)
        return round(numpy.mean(ttfb), self.decimal_precision)

    @cached_property
    @needs_numpy
    def page_load_time(self):
        """
        The average total load time for all runs (not weighted).
        """
        load_times = self.get_load_times('page')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    @needs_numpy
    def js_load_time(self):
        """
        Returns aggregate javascript load time.
        """
        load_times = self.get_load_times('js')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    @needs_numpy
    def css_load_time(self):
        """
        Returns aggregate css load time for all pages.
        """
        load_times = self.get_load_times('css')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    @needs_numpy
    def image_load_time(self):
        """
        Returns aggregate image load time for all pages.
        """
        load_times = self.get_load_times('image')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    @needs_numpy
    def html_load_time(self):
        """
        Returns aggregate html load time for all pages.
        """
        load_times = self.get_load_times('html')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    @needs_numpy
    def audio_load_time(self):
        """
        Returns aggregate audio load time for all pages.
        """
        load_times = self.get_load_times('audio')
        return round(numpy.mean(load_times), self.decimal_precision)

    @cached_property
    @needs_numpy
    def video_load_time(self):
        """
        Returns aggregate video load time for all pages.
        """
        load_times = self.get_load_times('video')
        return round(numpy.mean(load_times), self.decimal_precision)
