#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 14:40:53 MST
# File:    test_line_run.py

import pickle
import inspect
import tempfile

import pytest
import numpy as np

import z2pack

@pytest.fixture(params=np.linspace(-1, 1, 11))
def kz(request):
    return request.param

@pytest.fixture(params=[10**n for n in range(-4, -1)])
def pos_tol(request):
    return request.param

def test_trivial_run():
    sys = z2pack.em.System(lambda k: np.eye(4))
    line = lambda t: [0, 0, 0]
    result = z2pack.line.run(system=sys, line=line)
    assert result.wcc == [0, 0]
    assert result.gap_pos == 0.5
    assert result.gap_size == 1
    assert result.ctrl_states[z2pack._core.line._control.StepCounter] == 10
    assert result.ctrl_states[z2pack._core.line._control.WccConvergence] == dict(max_move=0, last_wcc=[0, 0])
    
def test_weyl(kz, compare_data):
    sys = z2pack.em.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    line = lambda t: [np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), kz]
    result = z2pack.line.run(system=sys, line=line)
    compare_data(lambda r1, r2: all(np.isclose(r1, r1).flatten()), result.wcc)

def test_no_pos_tol():
    sys = z2pack.em.System(lambda k: np.eye(4))
    line = lambda k: [0, 0, 0]
    result = z2pack.line.run(system=sys, line=line, pos_tol=None)
    assert result.wcc == [0, 0]
    assert result.gap_pos == 0.5
    assert result.gap_size == 1
    assert result.ctrl_states[z2pack._core.line._control.StepCounter] == 8
    with pytest.raises(KeyError):
        result.ctrl_states[z2pack._core.line._control.WccConvergence]

def test_pos_tol(kz, pos_tol, compare_equal):
    sys = z2pack.em.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    line = lambda t: [np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), kz]
    result = z2pack.line.run(system=sys, line=line, pos_tol=pos_tol)
    compare_equal(result.ctrl_states[z2pack._core.line._control.StepCounter])

def test_iterator():
    sys = z2pack.em.System(lambda k: np.eye(4))
    line = lambda k: [0, 0, 0]
    result = z2pack.line.run(system=sys, line=line, iterator=[5, 7, 9])
    assert result.ctrl_states[z2pack._core.line._control.StepCounter] == 7
    
def test_iterator_2():
    sys = z2pack.em.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    line = lambda t: [np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), 0.1]
    result = z2pack.line.run(system=sys, line=line, iterator=[4, 12, 21], pos_tol=1e-12)
    assert result.ctrl_states[z2pack._core.line._control.StepCounter] == 21
    
def test_iterator_3():
    sys = z2pack.em.System(lambda k: np.eye(4))
    line = lambda k: [0, 0, 0]
    result = z2pack.line.run(system=sys, line=line, iterator=[4, 12, 21], pos_tol=None)
    assert result.ctrl_states[z2pack._core.line._control.StepCounter] == 4

def assert_res_equal(result1, result2):
    assert result1.wcc == result2.wcc
    assert result1.gap_pos == result2.gap_pos
    assert result1.gap_size == result2.gap_size
    assert result1.ctrl_states.keys() == result2.ctrl_states.keys()
    for key in result1.ctrl_states:
        assert result1.ctrl_states[key] == result2.ctrl_states[key]

# saving tests
def test_simple_save():
    sys = z2pack.em.System(lambda k: np.eye(4))
    line = lambda k: [0, 0, 0]
    # This works only on Unix
    with tempfile.NamedTemporaryFile() as fp:
        result = z2pack.line.run(system=sys, line=line, save_file=fp.name)
        result2 = pickle.load(fp)
    assert_res_equal(result, result2)
    
def test_weyl_save(kz):
    sys = z2pack.em.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    line = lambda t: [np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), kz]
    # This works only on Unix
    with tempfile.NamedTemporaryFile() as fp:
        result = z2pack.line.run(system=sys, line=line, save_file=fp.name)
        result2 = pickle.load(fp)
    assert_res_equal(result, result2)
