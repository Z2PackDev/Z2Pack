#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.10.2014 11:51:20 CEST
# File:    test.py

import os
import re
import types
import unittest

expr = re.compile(r'\.py$')

"""
imports all classes inherited from unittest.TestCase from modules located
in the test folder
"""
exclude_list = ['test.py', 'create_tests.py']
for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    if(filename in exclude_list):
        continue
    match = expr.search(filename)
    if match is not None:
        for key, val in vars(__import__(filename[:match.start()])).items():
            try:
                if(issubclass(val, unittest.TestCase)):
                    vars()[key] = val
            except:
                pass

if __name__ == "__main__":
    print("Note: failures in test_res1 due to small numerical " +
    "differences are not a cause for concern.")
    unittest.main()
