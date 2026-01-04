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
	sphinx-apidoc --force -o docs/ haralyzer
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

test:
	py.test --cov haralyzer tests/ -vv


lint:
	black --check haralyzer
	pylint --disable=E1101,C0103,W0511,R0901,R0917 haralyzer
	flake8 --max-line-length 89 --statistics --show-source --count haralyzer
	bandit -r haralyzer


check-dist:
	pip install -U twine wheel setuptools build --quiet
	python setup.py egg_info
	python -m build --sdist --wheel .
	twine check --strict dist/*