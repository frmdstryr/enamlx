#!/usr/bin/env python
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Mar 2, 2016
"""
import re
from setuptools import setup, find_packages


def find_version():
    with open("enamlx/__init__.py") as f:
        for line in f:
            m = re.search(r'version = [\'"](.+)["\']', line)
            if m:
                return m.group(1)
    raise Exception("Could not find version in enamlx/__init__.py")


setup(
    name="enamlx",
    version=find_version(),
    description="Additional Qt Widgets for Enaml",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="frmdstryr",
    author_email="frmdstryr@gmail.com",
    url="https://github.com/frmdstryr/enamlx",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["enaml"],
    keywords=["enaml", "qt", "tree", "table", "widgets"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
