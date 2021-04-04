#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_reqs = [
    'cached-property',
    'python-dateutil',
]

test_requirements = [
    'pytest-cov',
    'coveralls',
    'bandit',
    'black>=20.8b1',
    'flake8',
    'pylint',
]

readme = open('README.rst').read()

setup(
        name='haralyzer',
        version='2.0.0',
        description='A python framework for getting useful stuff out of HAR files',
        long_description=readme,
        long_description_content_type="text/x-rst",
        author='Justin Crown',
        author_email='justincrown1@gmail.com',
        url='https://github.com/haralyzer/haralyzer',
        download_url='https://github.com/haralyzer/haralyzer/releases/latest',
        packages=[
            'haralyzer'
        ],
        package_dir={'haralyzer': 'haralyzer'},
        tests_require=test_requirements,
        install_requires=install_reqs,
        extras_require={
        },
        project_urls={
            'Changelog': 'https://github.com/haralyzer/haralyzer/blob/master/HISTORY.rst',
            'Issues': 'https://github.com/haralyzer/haralyzer/issues',
            'Releases': 'https://github.com/haralyzer/haralyzer/releases'
        },
        license='MIT',
        zip_safe=False,
        keywords='har',
        python_requires=">=3.6",
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
)
