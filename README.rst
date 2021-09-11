=========
Haralyzer
=========

.. image:: https://badge.fury.io/py/haralyzer.svg
   :target: http://badge.fury.io/py/haralyzer

.. image:: https://img.shields.io/pypi/dm/haralyzer
   :target: https://pypi.org/project/haralyzer/
   :alt: PyPI - Downloads

.. image:: https://img.shields.io/pypi/pyversions/haralyzer
   :target: https://pypi.org/project/haralyzer/
   :alt: PyPI - Python Version

.. image:: https://github.com/haralyzer/haralyzer/workflows/Python%20Checking/badge.svg
   :target: https://github.com/haralyzer/haralyzer/actions?query=workflow%3A%22Python+Checking%22

.. image:: https://coveralls.io/repos/github/haralyzer/haralyzer/badge.svg?branch=master
   :target: https://coveralls.io/github/haralyzer/haralyzer?branch=master

.. image:: https://readthedocs.org/projects/haralyzer/badge/?version=latest
   :target: https://haralyzer.readthedocs.org/en/latest/


A Python Framework For Using HAR Files To Analyze Web Pages.

Documentation
-------------

The documentation exists on `readthedocs <https://haralyzer.readthedocs.org/en/latest/>`_.

Overview
--------

The haralyzer module contains three classes for analyzing web pages based
on a HAR file. ``HarParser()`` represents a full file (which might have
multiple pages). ``HarPage()`` represents a single page from said file.
``HarEntry()`` represents an entry in a ``HarPage()``, and there are are multiple entries per page.
Each ``HarEntry`` has a request and response that contains items such as the headers, status code, timings, etc


Contributing
------------

We are always looking for new people to get involved. If you are looking to get involved, then fork this repo and start making changes that you would like to see.
If you are making any coding changes, then please create tests (we use pytest) for your code. Documentation should also be created for your additions. You can then submit a PR and we will review it.

Python 2 Support
++++++++++++++++

1.9.0. is the last version that supports Python 2.7.
