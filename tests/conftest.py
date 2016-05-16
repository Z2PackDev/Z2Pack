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
import operator
from collections.abc import Iterable

from ctrl_base_tester import test_ctrl_base

import z2pack
logging.getLogger('z2pack').setLevel(logging.CRITICAL)
from z2pack._utils import _get_max_move

def pytest_addoption(parser):
    parser.addoption('-A', action='store_true', help='run ABINIT tests')
    parser.addoption('-V', action='store_true', help='run VASP tests')
    parser.addoption('-Q', action='store_true', help='run Quantum ESPRESSO tests')

def pytest_configure(config):
    # register additional marker
    config.addinivalue_line("markers", "abinit: mark tests which run with ABINIT")
    config.addinivalue_line("markers", "vasp: mark tests which run with VASP")
    config.addinivalue_line("markers", "qe: mark tests which run with Quantum ESPRESSO")

def pytest_runtest_setup(item):
    abinit_marker = item.get_marker("abinit")
    vasp_marker = item.get_marker("vasp")
    qe_marker = item.get_marker("qe")
    if abinit_marker is not None:
        if not item.config.getoption("-A"):
            pytest.skip("test runs only with ABINIT")
    if vasp_marker is not None:
        if not item.config.getoption("-V"):
            pytest.skip("test runs only with VASP")
    if qe_marker is not None:
        if not item.config.getoption("-Q"):
            pytest.skip("test runs only with Quantum ESPRESSO")

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
    return lambda data, tag=None: compare_data(operator.eq, data, tag)

@pytest.fixture
def compare_wcc(compare_data):
    """Checks whether two lists of WCC (or nested lists of WCC) are almost equal, up to a periodic shift."""
    def check_wcc(wcc0, wcc1):
        if isinstance(wcc0[0], Iterable):
            if len(wcc0) != len(wcc1):
                return False
            return all(check_wcc(x, y) for x, y in zip(wcc0, wcc1))
        return _get_max_move(wcc0, wcc1) < 1e-8
    
    return lambda data, tag=None: compare_data(check_wcc, data, tag)
