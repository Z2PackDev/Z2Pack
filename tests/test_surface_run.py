#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.03.2016 10:29:04 CET
# File:    test_surface_run.py

import os
import json
import pickle
import msgpack
import tempfile

import pytest
import numpy as np

import z2pack

from em_systems import *

@pytest.fixture(params=range(5, 11, 2))
def num_strings(request):
    return request.param

@pytest.fixture(params=np.linspace(0.1, 0.4, 5))
def move_tol(request):
    return request.param

@pytest.fixture(params=[10**n for n in range(-5, -2)])
def pos_tol(request):
    return request.param

@pytest.fixture(params=[10**n for n in range(-4, -1)])
def gap_tol(request):
    return request.param

@pytest.fixture(params=[pickle, json, msgpack])
def serializer(request):
    z2pack.serializer.set(request.param)
    return request.param.__name__


def assert_res_equal(result1, result2):
    assert result1.wcc == result2.wcc
    assert all(np.isclose(result1.wilson, result2.wilson).flatten())
    assert result1.gap_size == result2.gap_size
    assert result1.gap_pos == result2.gap_pos
    assert result1.ctrl_states == result2.ctrl_states
    assert result1.convergence_report == result2.convergence_report

def test_simple(simple_system, simple_surface, num_strings):
    result = z2pack.surface.run(system=simple_system, surface=simple_surface, num_strings=num_strings)
    assert result.wcc == [[0, 0]] * num_strings
    assert result.gap_size == [1] * num_strings
    assert result.gap_pos == [0.5] * num_strings
    assert result.ctrl_states == {}

def test_neighbour_dist(weyl_system, weyl_surface):
    result = z2pack.surface.run(system=weyl_system, surface=weyl_surface, num_strings=11, min_neighbour_dist=0.09, move_tol=0., gap_tol=1.)
    assert len(result.wcc) == 11

def test_weyl(compare_data, compare_equal, pos_tol, gap_tol, move_tol, num_strings, weyl_system, weyl_surface):
    result = z2pack.surface.run(
        system=weyl_system,
        surface=weyl_surface,
        num_strings=num_strings,
        move_tol=move_tol,
        gap_tol=gap_tol,
        pos_tol=pos_tol
    )
    compare_data(lambda l1, l2: all(np.isclose(l1, l2).flatten()), result.wcc)
    compare_equal(result.convergence_report, tag='_report')

# saving tests
def test_simple_save(num_strings, simple_system, simple_surface):
    fp = tempfile.NamedTemporaryFile(delete=False)
    result1 = z2pack.surface.run(system=simple_system, surface=simple_surface, num_strings=num_strings, save_file=fp.name)
    result2 = z2pack.load_result(fp.name)
    os.remove(fp.name)
    assert_res_equal(result1, result2)

def test_weyl_save(pos_tol, gap_tol, move_tol, num_strings, weyl_system, weyl_surface):
    fp = tempfile.NamedTemporaryFile(delete=False)
    result1 = z2pack.surface.run(
        system=weyl_system,
        surface=weyl_surface,
        num_strings=num_strings,
        move_tol=move_tol,
        gap_tol=gap_tol,
        pos_tol=pos_tol,
        save_file=fp.name
    )
    result2 = z2pack.load_result(fp.name)
    os.remove(fp.name)
    assert_res_equal(result1, result2)

# test restart
def test_restart(simple_system, simple_surface):
    result1 = z2pack.surface.run(system=simple_system, surface=simple_surface)
    result2 = z2pack.surface.run(system=simple_system, surface=simple_surface, init_result=result1)
    assert_res_equal(result1, result2)

# test that restart doesn't recalculate
def test_restart_nocalc(simple_system, simple_surface):
    class Mock:
        def get_eig(self, *args, **kwargs):
            raise ValueError('This restart should not re-compute anything!')
    result1 = z2pack.surface.run(system=simple_system, surface=simple_surface)
    result2 = z2pack.surface.run(system=Mock(), surface=simple_surface, init_result=result1)
    assert_res_equal(result1, result2)

# test restart with smaller precision
def test_restart_2(weyl_system, weyl_surface):
    result1 = z2pack.surface.run(system=weyl_system, surface=weyl_surface)
    result2 = z2pack.surface.run(system=weyl_system, surface=weyl_surface, pos_tol=0.5, gap_tol=1e-1, move_tol=0.5, num_strings=6)
    result2 = z2pack.surface.run(system=weyl_system, surface=weyl_surface, init_result=result2)
    assert_res_equal(result1, result2)

def test_invalid_restart(simple_system, simple_surface):
    result = z2pack.surface.run(system=simple_system, surface=simple_surface)
    with pytest.raises(ValueError):
        result2 = z2pack.surface.run(system=simple_system, surface=simple_surface, init_result=result, load=True)

def test_file_restart(simple_system, simple_surface, serializer):
    with tempfile.NamedTemporaryFile() as fp:
        result = z2pack.surface.run(system=simple_system, surface=simple_surface, save_file=fp.name)
        result2 = z2pack.surface.run(system=simple_system, surface=simple_surface, save_file=fp.name, load=True)
    assert_res_equal(result, result2)
    
def test_load_inexisting(simple_system, simple_surface):
    with pytest.raises(IOError):
        result = z2pack.surface.run(system=simple_system, surface=simple_surface, save_file='invalid_name', load_quiet=False, load=True)

def test_load_inconsistent(simple_system, simple_surface):
    with pytest.raises(ValueError):
        result = z2pack.surface.run(system=simple_system, surface=simple_surface, init_result='bla', save_file='invalid_name', load=True)
        
def test_load_no_filename(simple_system, simple_surface, serializer):
    with pytest.raises(ValueError):
        result = z2pack.surface.run(system=simple_system, surface=simple_surface, load=True)
