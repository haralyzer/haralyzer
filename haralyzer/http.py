"""Creates the Request and Response sub class that are used by each entry"""
from typing import Optional
from cached_property import cached_property
from .mixins import HttpTransaction


class Request(HttpTransaction):
    """Request object for an HarEntry"""

    def __str__(self):
        return f"HarEntry.Request for {self.url}"

    def __repr__(self):
        return f"HarEntry.Request for {self.url}"

    # Root Level values

    @cached_property
    def bodySize(self) -> int:
        """
        :return: Body size of the request
        :rtype: int
        """
        return self.raw_entry["bodySize"]

    @cached_property
    def cookies(self) -> list:
        """
        :return: Cookies from the request
        :rtype: list
        """
        return self.raw_entry["cookies"]

    @cached_property
    def headersSize(self) -> int:
        """
        :return: Headers size from the request
        :rtype: int
        """
        return self.raw_entry["headersSize"]

    @cached_property
    def httpVersion(self) -> str:
        """
        :return: HTTP version used in the request
        :rtype: str
        """
        return self.raw_entry["httpVersion"]

    @cached_property
    def method(self) -> str:
        """
        :return: HTTP method of the request
        :rtype: str
        """
        return self.raw_entry["method"]

    @cached_property
    def queryString(self) -> list:
        """
        :return: Query string from the request
        :rtype: list
        """
        return self.raw_entry["queryString"]

    @cached_property
    def url(self) -> str:
        """
        :return: URL of the request
        :rtype: str
        """
        return self.raw_entry["url"]

    # Header Values

    @cached_property
    def accept(self) -> str:
        """
        :return: HTTP Accept header
        :rtype: str
        """
        return self.get_header_value("Accept")

    @cached_property
    def cacheControl(self) -> str:
        """
        :return: HTTP CacheControl header
        :rtype: str
        """
        return self.get_header_value("Cache-Control")

    @cached_property
    def encoding(self) -> str:
        """
        :return: HTTP Accept-Encoding Header
        :rtype: str
        """
        return self.get_header_value("Accept-Encoding")

    @cached_property
    def host(self) -> str:
        """
        :return: HTTP Host header
        :rtype: str
        """
        return self.get_header_value("Host")

    @cached_property
    def language(self) -> str:
        """
        :return: HTTP language header
        :rtype: str
        """
        return self.get_header_value("Accept-Language")

    @cached_property
    def userAgent(self) -> str:
        """
        :return: User Agent
        :rtype: str
        """
        return self.get_header_value("User-Agent")


class Response(HttpTransaction):
    """Response object for a HarEntry"""

    def __init__(self, url: str, entry: dict):
        """

        :param url: Responses don't have a URL so need to get it passed
        :type url: str
        :param entry: Response data
        """
        super().__init__(entry)
        self.url = url

    def __str__(self) -> str:
        return f"HarEntry.Response for {self.url}"

    def __repr__(self) -> str:
        return f"HarEntry.Response for {self.url}"

    # Root Level values

    @cached_property
    def bodySize(self) -> int:
        """
        :return: Body Size
        :rtype: int
        """
        return self.raw_entry["bodySize"]

    @cached_property
    def headersSize(self) -> int:
        """
        :return: Header size
        :rtype: int
        """
        return self.raw_entry["headersSize"]

    @cached_property
    def httpVersion(self) -> str:
        """
        :return: HTTP Version
        :rtype: str
        """
        return self.raw_entry["httpVersion"]

    @cached_property
    def redirectURL(self) -> Optional[str]:
        """
        :return: Redirect URL
        :rtype: Optional[str]
        """
        return self.raw_entry.get("redirectURL", None)

    @cached_property
    def status(self) -> int:
        """
        :return:HTTP Status
        :rtype: int
        """
        return self.raw_entry["status"]

    @cached_property
    def statusText(self) -> str:
        """
        :return: HTTP Status Text
        :rtype: str
        """
        return self.raw_entry["statusText"]

    # Header Values

    @cached_property
    def cacheControl(self) -> str:
        """
        :return: Cache Control Header
        :rtype: str
        """
        return self.get_header_value("cache-control")

    @cached_property
    def contentSecurityPolicy(self) -> str:
        """
        :return: Content Security Policy Header
        :rtype: str
        """
        return self.get_header_value("content-security-policy")

    @cached_property
    def contentSize(self) -> int:
        """
        :return: Content Size
        :rtype: int
        """
        return self.raw_entry["content"]["size"]

    @cached_property
    def contentType(self) -> str:
        """
        :return: Content Type
        :rtype: str
        """
        return self.get_header_value("content-type")

    @cached_property
    def date(self) -> str:
        """
        :return:Date of response
        :rtype: str
        """
        return self.get_header_value("date")

    @cached_property
    def lastModified(self) -> str:
        """
        :return: Last modified time
        :rtype: str
        """
        return self.get_header_value("last-modified")

    @cached_property
    def mimeType(self) -> str:
        """
        :return: Mime Type of response
        :rtype: str
        """
        return self.raw_entry["content"]["mimeType"]

    @cached_property
    def text(self) -> str:
        """
        :return: Response body
        :rtype: str
        """
        return self.raw_entry["content"]["text"]
