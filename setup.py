#!/usr/bin/env python
import codecs
import os.path
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r'^__version__ = "([^"]+)"',
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def borrow_requirements():
    with open(os.path.join(here, "requirements.txt")) as source:
        return [line.strip() for line in filter(None, source.readlines())]


setup_options = dict(
    name="awsr",
    version=find_version("awsr", "__init__.py"),
    description="Renew AWS Access Key",
    long_description=read("README.rst"),
    author="Alyson Tiago S. Ferreira",
    url="https://github.com/alyson-ferreira/awsr",
    scripts=["bin/awsr"],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=borrow_requirements(),
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
)

setup(**setup_options)
