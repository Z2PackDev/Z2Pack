#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.02.2016 18:07:11 MST
# File:    conftest.py

import os
import pytest
import pickle

from ctrl_base_tester import test_ctrl_base

@pytest.fixture
def test_name(request):
    """Returns module_name.function_name for a given test"""
    return request.module.__name__ + '/' + request._parent_request._pyfuncitem.name

@pytest.fixture
def compare_data(request, test_name, scope="session"):
    """Returns a function which either saves some data to a file or (if that file exists already) compares it to pre-existing data using a given comparison function."""
    def inner(compare_fct, data):
        val = request.config.cache.get(test_name, None)
        if val is None:
            request.config.cache.set(test_name, data)
            raise ValueError('Reference data does not exist.')
        else:
            assert compare_fct(val, data)
    return inner

@pytest.fixture
def compare_equal(compare_data):
    return lambda data: compare_data(lambda x, y: x == y, data)
