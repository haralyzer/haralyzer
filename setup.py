#!/usr/bin/env python
from setuptools import setup

install_reqs = open("requirements.txt").readlines()
test_reqs = open("requirements-dev.txt").readlines()


readme = open('README.rst').read()

setup(
        name='haralyzer',
        version='2.2.0',
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
        tests_require=test_reqs[1:],
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
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: Implementation :: CPython'
        ],
)
