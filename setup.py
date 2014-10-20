#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.10.2014 11:27:40 CEST
# File:    setup.py

from distutils.core import setup

setup(  name = 'z2pack',
        version = '0.1',
        url = '',
        author = 'Dominik Gresch',
        author_email = 'greschd@gmx.ch',
        description = 'A tool for calculating topological invariants',
        license = 'LICENSE.txt',
        packages = ['z2pack',
                    'z2pack.python_tools',
                    'z2pack.tb',
                    'z2pack.fp']
)
