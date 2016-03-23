#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.02.2016 18:07:11 MST
# File:    conftest.py

import os
import json
import pytest
import pickle
import logging

from ctrl_base_tester import test_ctrl_base

import z2pack
logging.getLogger('z2pack').setLevel(logging.CRITICAL)

@pytest.fixture
def test_name(request):
    """Returns module_name.function_name for a given test"""
    return request.module.__name__ + '/' + request._parent_request._pyfuncitem.name

@pytest.fixture
def compare_data(request, test_name, scope="session"):
    """Returns a function which either saves some data to a file or (if that file exists already) compares it to pre-existing data using a given comparison function."""
    def inner(compare_fct, data, tag=None):
        full_name = test_name + (tag or '')
        val = request.config.cache.get(full_name, None)
        if val is None:
            request.config.cache.set(full_name, data)
            raise ValueError('Reference data does not exist.')
        else:
            assert compare_fct(val, json.loads(json.dumps(data))) # get rid of json-specific quirks
    return inner

@pytest.fixture
def compare_equal(compare_data):
    return lambda data, tag=None: compare_data(lambda x, y: x == y, data, tag)
