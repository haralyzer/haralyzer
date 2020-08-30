"""Creates the Request and Response sub class that are used by each entry"""
from cached_property import cached_property


class Request(object):
    """Request Object for an entry"""
    def __init__(self, entry: dict):
        self.raw_entry = entry

    def get_header_value(self, name: str) -> str:
        for x in self.raw_entry["headers"]:
            if x["name"] == name:
                return x["value"]
        return ""

    # Root Level values

    @cached_property
    def bodySize(self) -> int:
        return self.raw_entry["bodySize"]

    @cached_property
    def method(self) -> str:
        return self.raw_entry["method"]

    @cached_property
    def url(self) -> str:
        return self.raw_entry["url"]

    @cached_property
    def headers(self) -> list:
        return self.raw_entry["headers"]

    @cached_property
    def httpVersion(self) -> str:
        return self.raw_entry["httpVersion"]

    @cached_property
    def queryString(self) -> list:
        return self.raw_entry["queryString"]

    @cached_property
    def headersSize(self) -> int:
        return self.raw_entry["headersSize"]

    @cached_property
    def cookies(self) -> list:
        return self.raw_entry["cookies"]

    # Header Values

    @cached_property
    def host(self) -> str:
        return self.get_header_value("Host")

    @cached_property
    def userAgent(self) -> str:
        return self.get_header_value("User-Agent")

    @cached_property
    def accept(self) -> str:
        return self.get_header_value("Accept")

    @cached_property
    def language(self) -> str:
        return self.get_header_value("Accept-Language")

    @cached_property
    def encoding(self) -> str:
        return self.get_header_value("Accept-Encoding")

    @cached_property
    def cacheControl(self) -> str:
        return self.get_header_value("Cache-Control")


class Response(object):
    """Entry Response"""
    def __init__(self, entry: dict):
        self.raw_entry = entry

    def get_header_value(self, name: str) -> str:
        for x in self.raw_entry["headers"]:
            if x["name"] == name:
                return x["value"]
        return ""

    # Root Level values

    @cached_property
    def status(self) -> int:
        return self.raw_entry["status"]

    @cached_property
    def statusText(self) -> str:
        return self.raw_entry["statusText"]

    @cached_property
    def httpVersion(self) -> str:
        return self.raw_entry["httpVersion"]

    @cached_property
    def headers(self) -> list:
        return self.raw_entry["headers"]

    @cached_property
    def redirectURL(self) -> [str, None]:
        if self.raw_entry["redirectURL"]:
            return self.raw_entry["redirectURL"]
        return None

    @cached_property
    def headersSize(self) -> int:
        return self.raw_entry["headersSize"]

    @cached_property
    def bodySize(self) -> int:
        return self.raw_entry["bodySize"]

    # Header Values

    @cached_property
    def date(self) -> str:
        return self.get_header_value("date")

    @cached_property
    def contentType(self) -> str:
        return self.get_header_value("content-type")

    @cached_property
    def cacheControl(self) -> str:
        return self.get_header_value("cache-control")

    @cached_property
    def lastModified(self) -> str:
        return self.get_header_value("last-modified")

    @cached_property
    def contentSecurityPolicy(self):
        return self.get_header_value("content-security-policy")

    @cached_property
    def contentSize(self) -> int:
        return self.raw_entry["content"]["size"]

    @cached_property
    def mimeType(self) -> str:
        return self.raw_entry['content']['mimeType']

    @cached_property
    def text(self) -> str:
        return self.raw_entry['content']['text']


