# -*- coding: utf-8; -*-
"""Contains compatibility functions extracted from the 'six' project."""
from six import PY3

if PY3:

    def iteritems(d, **kw):
        """Iterate through dictionary items"""
        return iter(d.items(**kw))


else:

    def iteritems(d, **kw):
        """Iterate through dictionary items"""
        return iter(d.iteritems(**kw))
