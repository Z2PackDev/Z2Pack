#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.02.2016 18:07:11 MST
# File:    conftest.py

import os
import pytest
import pickle

@pytest.fixture
def test_name(request):
    """Returns module_name.function_name for a given test"""
    return request.module.__name__ + '.' + request.function.__name__

@pytest.fixture
def compare_data(test_name, scope="session"):
    """Returns a function which either saves some data to a file or (if that file exists already) compares it to pre-existing data using a given comparison function."""
    cache_dir = os.path.abspath(os.path.dirname(__file__)) + '/cache_data/'
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    savefile_base =  cache_dir + test_name + '.p'
    def inner(compare_fct, data=None, tag=None):
        # create savefile name
        if tag is None:
            tag = ''
        else:
            tag = '_' + tag
        savefile = savefile_base + tag
        # read data if it exists and compare
        if os.path.isfile(savefile):
            with open(savefile, 'rb') as f:
                ref_data = pickle.load(f)
            assert compare_fct(data, ref_data)
        else:
            with open(savefile, 'wb') as f:
                pickle.dump(data, f)
            raise ValueError('Reference data does not exist.')
    return inner

@pytest.fixture
def compare_equal(compare_data, scope='session'):
    """Returns a function which either saves some data to a file or (if that file exists already) compares it for equality to the pre-existing data."""
    def inner(*args, **kwargs):
        return compare_data(lambda x, y: x == y, *args, **kwargs)

    return inner
