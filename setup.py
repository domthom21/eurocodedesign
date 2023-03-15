#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Dominik Thomas",
    author_email='dominik.thomas@hsu-hh.de',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
    ],
    description="Typed python framework for eurocode calculations.",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='eurocodedesign',
    name='eurocodedesign',
    packages=find_packages(include=['eurocodedesign', 'eurocodedesign.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/domthom21/eurocodedesign',
    version='0.0.1',
    zip_safe=False,
)
