.PHONY: clean clean-build clean-pyc test docs

clean: clean-build clean-pyc

clean-build:
	$(RM) -r build/
	$(RM) -r dist/
	$(RM) -r *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec $(RM) {} +
	find . -name '*.pyo' -exec $(RM) {} +
	find . -name '*~' -exec $(RM) {} +

docs:
	$(RM) docs/haralyzer.rst
	$(RM) docs/modules.rst
	sphinx-apidoc -o docs/ haralyzer
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

test:
	py.test tests/
