.. haralyzer documentation master file, created by
   sphinx-quickstart on Thu Feb 26 08:00:24 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========
Haralyzer
=========

.. image:: https://badge.fury.io/py/haralyzer.svg
    :target: http://badge.fury.io/py/haralyzer

Haralyzer is a Python framework for using HAR files to analyze web pages.

Overview
--------

The haralyzer module contains three classes for analyzing web pages based
on a HAR file. ``HarParser()`` represents a full file (which might have
multiple pages). ``HarPage()`` represents a single page from said file.
``HarEntry()`` represents an entry in a ``HarPage()``, and there are are multiple entries per page.
Each ``HarEntry`` has a request and response that contains items such as the headers, status code, timings, etc

``HarParser`` has a couple of helpful methods for analyzing single entries
from a HAR file, but most of the pertinent functions are inside of the page
object.

``haralyzer`` was designed to be easy to use, but you can also access more
powerful functions directly.

Basic Usage
-----------
.. toctree::
   :maxdepth: 2

   basic/harparser
   basic/harpage
   basic/harentry

Advanced
--------
.. toctree::
   :maxdepth: 2

   advanced/harpage
   advanced/asset_timeline



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

