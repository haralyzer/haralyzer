#!/usr/bin/env python
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_reqs = ['cached-property',
                'python-dateutil', ]
if sys.version_info < (3, 4):
    install_reqs.extend([
        "backports.statistics",
    ])
test_requirements = ['pytest-cov',
                     'python-coveralls', ]

readme = open('README.rst').read()

setup(
        name='haralyzer',
        version='1.7.0',
        description='A python framework for getting useful stuff out of HAR files',
        long_description=readme,
        author='Justin Crown',
        author_email='justincrown1@gmail.com',
        url='https://github.com/mrname/haralyzer',
        download_url='https://github.com/mrname/haralyzer/tarball/1.0',
        packages=[
            'haralyzer'
        ],
        package_dir={'haralyzer': 'haralyzer'},
        tests_require=test_requirements,
        install_requires=install_reqs,
        extras_require={
        },
        license='MIT',
        zip_safe=False,
        keywords='har',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 2.7',
        ],
)
