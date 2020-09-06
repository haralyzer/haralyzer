"""Mixin Objects that allow for shared methods"""
from abc import ABC
from cached_property import cached_property

from six.moves.collections_abc import MutableMapping


class GetHeaders(object):
    """Mixin to get a header"""
    def get_header_value(self, name):
        """
        Returns the header value of the header defined in ``name``

        :param name: ``str`` name of the header to get the value of
        """
        for x in self.raw_entry["headers"]:
            if x["name"].lower() == name.lower():
                return x["value"]


class MimicDict(MutableMapping, ABC):
    """Mixin for functions to mimic a dictionary for backward compatibility"""

    def __getitem__(self, item):
        return self.raw_entry[item]

    def __len__(self):
        return len(self.raw_entry)

    def __delitem__(self, key):
        del self.raw_entry[key]

    def __iter__(self):
        return iter(self.raw_entry)

    def __setitem__(self, key, value):
        self.raw_entry[key] = value


class HttpTransaction(GetHeaders, MimicDict):
    def __init__(self, entry):
        self.raw_entry = entry

    # Base class gets properties that belong to both request/response
    @cached_property
    def headers(self):
        return self.raw_entry["headers"]
