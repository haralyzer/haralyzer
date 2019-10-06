.. :changelog

History
-------

1.7.1 (2019-10-06)
++++++++++++++++++

* BUGFIX - Default to empty string if a page has not title.
  Provided by @pckizer.

1.7.00 (2019-10-06)
++++++++++++++++++

* Added `duplicate_url_requests` method provided by @gowthamraj198.

1.6.00 (2019-01-05)
++++++++++++++++++

* Resolved issue with entries in HAR files which do not belong to a page. The
  new behavior will create a "fake" HarPage with an ID of "unknown" if one or
  more of these entries exist, and add them to it. Ths will allow the overall
  HarParser to still take these entries into account for timings.

1.5.00 (2018-07-18)
++++++++++++++++++

* python 3.7 compatibility. Specifically, removing the keyword `async` which is now a reserved keyword
  argument. As of right now, we are still maintaining backwards compatability, but it is deprecated and
  will be removed in a future version. You should now use `asynchronous` instead. Many thanks to
  NickPancakes for hooking it up.

1.4.11 (2017-11-14)
+++++++++++++++++++

* Adding methods for retreiving transferred size of assets (with compression)

1.4.6 (2016-04-01)
++++++++++++++++++

* Bugfix for maximum recursion depth being hit when HarPage is initialized with a page
  ID that does not exist in the HAR file.

1.4.5 (2016-03-22)
++++++++++++++++++

* Removing numpy as a requirement

1.1.0 (2015-03-22)
++++++++++++++++++

* Using @cached_property instead of @property
* Small refactor to logic behind getting property values
* Increased test coverage

1.0.8 (2015-03-01)
++++++++++++++++++

* Adding coveralls + Travis integration

1.0.7 (2015-03-01)
++++++++++++++++++

* Adding pypi badge to README

1.0.2 - 1.0.6 (2015-03-01)
++++++++++++++++++

* Tweaking docs for pypi

1.0.1 (2015-03-01)
++++++++++++++++++

* Adding Travis CI integration

1.0 (2015-02-28)
++++++++++++++++

* Initial Beta release
