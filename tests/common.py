#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 10:18:11 CEST
# File:    common.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/../')
import z2pack
try:
    from z2pack.ptools.replace import *
except ImportError:
    pass

import types
import inspect
import warnings
warnings.simplefilter('always')

import unittest
# ugly hack to enable in-place replacement of arrays
from numpy import array

def assertFullAlmostEqual(TestCase, x, y):
    """
    Compares for almost equality
    """
    # str
    if isinstance(x, str):
        TestCase.assertEqual(x, y)
    # dict
    elif hasattr(x, 'keys'):
        if not(sorted(x.keys()) == sorted(y.keys())):
            TestCase.fail(msg="dicts don't have the same keys")
        for key in x.keys():
            TestCase.assertFullAlmostEqual(x[key], y[key])
    # list, tuple
    elif hasattr(x, '__iter__'):
        if len(x) != len(y):
            TestCase.fail(msg='length of objects is not equal')
        for xval, yval in zip(x, y):
            TestCase.assertFullAlmostEqual(xval, yval)
    # rest
    else:
        try:
            TestCase.assertAlmostEqual(x, y)
        except TypeError:
            TestCase.assertEqual(x, y)

def assertFullEqual(TestCase, x, y):
    """
    Compares for almost equality
    """
    # str
    if isinstance(x, str):
        TestCase.assertEqual(x, y)
    # dict
    elif hasattr(x, 'keys'):
        if not(sorted(x.keys()) == sorted(y.keys())):
            TestCase.fail(msg="dicts don't have the same keys")
        for key in x.keys():
            TestCase.assertFullEqual(x[key], y[key])
    # list, tuple
    elif hasattr(x, '__iter__'):
        if len(x) != len(y):
            TestCase.fail(msg='length of objects is not equal')
        for xval, yval in zip(x, y):
            TestCase.assertFullEqual(xval, yval)
    # rest
    else:
        TestCase.assertEqual(x, y)

class CommonTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(CommonTestCase, self).__init__(*args, **kwargs)
        self.assertFullAlmostEqual = types.MethodType(
            assertFullAlmostEqual, self)
        self.assertFullEqual = types.MethodType(
            assertFullEqual, self)
