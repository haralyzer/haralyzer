"""Creates the Request and Response sub class that are used by each entry"""
from cached_property import cached_property
from .mixins import HttpTransaction


class Request(HttpTransaction):
    """Request object for an HarEntry"""

    def __str__(self):
        return "HarEntry.Request for %s" % self.raw_entry["url"]

    def __repr__(self):
        return "HarEntry.Request for %s" % self.raw_entry["url"]

    # Root Level values

    @cached_property
    def bodySize(self):
        """Body size of the request"""
        return self.raw_entry["bodySize"]

    @cached_property
    def cookies(self):
        """Cookies from the request"""
        return self.raw_entry["cookies"]

    @cached_property
    def headersSize(self):
        """Headers size from the request"""
        return self.raw_entry["headersSize"]

    @cached_property
    def httpVersion(self):
        """HTTP version used in the request"""
        return self.raw_entry["httpVersion"]

    @cached_property
    def method(self):
        """HTTP method of the request"""
        return self.raw_entry["method"]

    @cached_property
    def queryString(self):
        """Query string from the request"""
        return self.raw_entry["queryString"]

    @cached_property
    def url(self):
        """URL of the request"""
        return self.raw_entry["url"]

    # Header Values

    @cached_property
    def accept(self):
        """HTTP Accept header"""
        return self.get_header_value("Accept")

    @cached_property
    def cacheControl(self):
        """HTTP CacheControl header"""
        return self.get_header_value("Cache-Control")

    @cached_property
    def encoding(self):
        """HTTP Accept-Encoding Header"""
        return self.get_header_value("Accept-Encoding")

    @cached_property
    def host(self):
        """HTTP Host header"""
        return self.get_header_value("Host")

    @cached_property
    def language(self):
        """HTTP language header"""
        return self.get_header_value("Accept-Language")

    @cached_property
    def userAgent(self):
        """User Agent """
        return self.get_header_value("User-Agent")


class Response(HttpTransaction):
    """Response object for a HarEntry"""

    def __str__(self):
        return "HarEntry.Response for %s" % self.raw_entry["url"]

    def __repr__(self):
        return "HarEntry.Response for %s" % self.raw_entry["url"]

    # Root Level values

    @cached_property
    def bodySize(self):
        """Body Szie"""
        return self.raw_entry["bodySize"]

    @cached_property
    def headersSize(self):
        """Header size"""
        return self.raw_entry["headersSize"]

    @cached_property
    def httpVersion(self):
        """HTTP Version"""
        return self.raw_entry["httpVersion"]

    @cached_property
    def redirectURL(self):
        """Redirect URL"""
        return self.raw_entry.get("redirectURL", None)

    @cached_property
    def status(self):
        """HTTP Status"""
        return self.raw_entry["status"]

    @cached_property
    def statusText(self):
        """HTTP Status Text"""
        return self.raw_entry["statusText"]

    # Header Values

    @cached_property
    def cacheControl(self):
        """Cache Control Header"""
        return self.get_header_value("cache-control")

    @cached_property
    def contentSecurityPolicy(self):
        """Content Security Policy Header"""
        return self.get_header_value("content-security-policy")

    @cached_property
    def contentSize(self):
        """Content Size"""
        return self.raw_entry["content"]["size"]

    @cached_property
    def contentType(self):
        """Content Type"""
        return self.get_header_value("content-type")

    @cached_property
    def date(self):
        """Date of response"""
        return self.get_header_value("date")

    @cached_property
    def lastModified(self):
        """Last modified time"""
        return self.get_header_value("last-modified")

    @cached_property
    def mimeType(self):
        """Mime Type of response"""
        return self.raw_entry["content"]["mimeType"]

    @cached_property
    def text(self):
        """Response body"""
        return self.raw_entry["content"]["text"]
