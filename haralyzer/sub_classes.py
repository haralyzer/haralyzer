"""Creates the Request and Response sub class that are used by each entry"""
from cached_property import cached_property


class Request(object):
    """Request object for an HarEntry"""
    def __init__(self, entry):
        self.raw_entry = entry

    def get_header_value(self, name):
        for x in self.raw_entry["headers"]:
            if x["name"].lower() == name.lower():
                return x["value"]

    # Root Level values

    @cached_property
    def bodySize(self):
        return self.raw_entry["bodySize"]

    @cached_property
    def method(self):
        return self.raw_entry["method"]

    @cached_property
    def url(self):
        return self.raw_entry["url"]

    @cached_property
    def headers(self):
        return self.raw_entry["headers"]

    @cached_property
    def httpVersion(self):
        return self.raw_entry["httpVersion"]

    @cached_property
    def queryString(self):
        return self.raw_entry["queryString"]

    @cached_property
    def headersSize(self):
        return self.raw_entry["headersSize"]

    @cached_property
    def cookies(self):
        return self.raw_entry["cookies"]

    # Header Values

    @cached_property
    def host(self):
        return self.get_header_value("Host")

    @cached_property
    def userAgent(self):
        return self.get_header_value("User-Agent")

    @cached_property
    def accept(self):
        return self.get_header_value("Accept")

    @cached_property
    def language(self):
        return self.get_header_value("Accept-Language")

    @cached_property
    def encoding(self):
        return self.get_header_value("Accept-Encoding")

    @cached_property
    def cacheControl(self):
        return self.get_header_value("Cache-Control")


class Response(object):
    """Response object for a HarEntry"""
    def __init__(self, entry):
        self.raw_entry = entry

    def get_header_value(self, name):
        for x in self.raw_entry["headers"]:
            if x["name"].lower() == name.lower():
                return x["value"]

    # Root Level values

    @cached_property
    def status(self):
        return self.raw_entry["status"]

    @cached_property
    def statusText(self):
        return self.raw_entry["statusText"]

    @cached_property
    def httpVersion(self):
        return self.raw_entry["httpVersion"]

    @cached_property
    def headers(self):
        return self.raw_entry["headers"]

    @cached_property
    def redirectURL(self):
        if self.raw_entry["redirectURL"]:
            return self.raw_entry["redirectURL"]

    @cached_property
    def headersSize(self):
        return self.raw_entry["headersSize"]

    @cached_property
    def bodySize(self):
        return self.raw_entry["bodySize"]

    # Header Values

    @cached_property
    def date(self):
        return self.get_header_value("date")

    @cached_property
    def contentType(self):
        return self.get_header_value("content-type")

    @cached_property
    def cacheControl(self) -> str:
        return self.get_header_value("cache-control")

    @cached_property
    def lastModified(self):
        return self.get_header_value("last-modified")

    @cached_property
    def contentSecurityPolicy(self):
        return self.get_header_value("content-security-policy")

    @cached_property
    def contentSize(self):
        return self.raw_entry["content"]["size"]

    @cached_property
    def mimeType(self):
        return self.raw_entry['content']['mimeType']

    @cached_property
    def text(self):
        return self.raw_entry['content']['text']


