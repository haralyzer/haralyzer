"""
Custom exceptions for good ol haralyzer.
"""


class PageNotFoundError(AttributeError):
    """
    Raised when a page cannot be found with the given page ID.
    """
    pass

class PageLoadTimeError(ValueError):
    """
    Raised when full page load time (including browser execution) cannot be
    obtained. When this is raised, you can catch it and use
    HarPage.asset_load_time instead, which is the total load time of all of the
    assets on the page, but does not including things like JS execution.
    """
    pass
