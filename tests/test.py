#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.10.2014 11:51:20 CEST
# File:    test.py


import os
import re
import sys
import types
import shutil
import unittest
import argparse

from common import *


"""
imports all classes inherited from unittest.TestCase from modules located
in the test folder (fp tests can be switched on or off).
"""

if __name__ == "__main__":
    try:
        shutil.rmtree('build')
    except OSError:
        pass
    os.mkdir('build')

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vasp', action='store_true', dest='vasp')
    parser.add_argument('-e', '--espresso', action='store_true', dest='espresso')
    parser.add_argument('-a', '--abinit', action='store_true', dest='abinit')
    arguments = parser.parse_args(sys.argv[1:])
    sys.argv = [sys.argv[0]] 

    special_cases = [(VaspTestCase, arguments.vasp),
                     (AbinitTestCase, arguments.abinit),
                     (EspressoTestCase, arguments.espresso)]

    expr = re.compile(r'\.py$')
    exclude_list = ['test.py', 'create_tests.py']
    for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        if(filename in exclude_list):
            continue
        match = expr.search(filename)
        if match is not None:
            for key, val in vars(__import__(filename[:match.start()])).items():
                try:
                    if issubclass(val, unittest.TestCase):
                        if all([(not issubclass(val, case[0])) or case[1] for case in special_cases]):
                            vars()[key] = val
                except:
                    pass

    print("Note: Tests including iterative steps may fail due to " +
    "small numerical \n      differences. This is not a cause for concern")
    unittest.main()
