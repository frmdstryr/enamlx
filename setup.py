#!/usr/bin/env python
'''
Created on Mar 2, 2016

@author: frmdstryr
'''
from setuptools import setup,find_packages

setup(
    name='enamlx',
    version='0.1',
    description='Additional Qt Widgets for Enaml',
    long_description=open('README.md').read(),
    author='frmdstryr',
    author_email='frmdstryr@gmail.com',
    license=open('LICENSE').read(),
    url='https://github.com/frmdstryr/enamlx',
    download_url='https://github.com/frmdstryr/enamlx/archive/master.zip',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['enaml'],
    zip_safe=False,
    keywords=['enaml', 'qt', 'tree', 'table','widgets'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',        
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)