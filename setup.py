#!/usr/bin/env python
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Mar 2, 2016
"""
from setuptools import setup, find_packages

setup(
    name='enamlx',
    version='0.2.5',
    description='Additional Qt Widgets for Enaml',
    long_description=open('README.md').read(),
    author='frmdstryr',
    author_email='frmdstryr@gmail.com',
    url='https://github.com/frmdstryr/enamlx',
    download_url='https://github.com/frmdstryr/enamlx/',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['enaml'],
    zip_safe=False,
    keywords=['enaml', 'qt', 'tree', 'table', 'widgets'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',        
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
