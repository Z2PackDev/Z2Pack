#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.10.2014 11:27:40 CEST
# File:    setup.py

try:
    from setuptools import setup
except:
    from distutils.core import setup

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='z2pack',
    version='1.0',
    url='http://z2pack.ethz.ch',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    description='A tool for calculating topological invariants',
    install_requires=['matplotlib', 'decorator'],
    long_description=readme,
    license='LICENSE.txt',
    packages=['z2pack',
              'z2pack.ptools',
              'z2pack.tb',
              'z2pack.fp'])
