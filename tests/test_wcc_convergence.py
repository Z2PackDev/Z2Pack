#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.02.2016 18:14:05 MST
# File:    test_stepcounter.py

import inspect

import pytest
import numpy as np

import z2pack
from z2pack._core.line._control import WccConvergence
from monkeypatch_data import *

def test_base(test_ctrl_base):
    test_ctrl_base(WccConvergence)
    assert issubclass(WccConvergence, z2pack._core._control_base.LineControl)

# Monkeypatching s.t. the data.wcc is just a float, and _get_max_move is just min(wcc1, wcc2)

@pytest.fixture
def patch_max_move(monkeypatch):
    monkeypatch.setattr(z2pack._core.line._control, '_get_max_move', min)

@pytest.fixture(params=np.linspace(0.01, 0.99, 21))
def pos_tol(request):
    return request.param

def test_one_step(pos_tol, patch_max_move, patch_line_data):
    wc = WccConvergence(pos_tol=pos_tol)
    wc.update(LineData(0.1))
    assert not wc.converged

def test_one_step_init(pos_tol, patch_max_move, patch_line_data):
    wc = WccConvergence(pos_tol=pos_tol)
    wc.state = dict(max_move=pos_tol * 1.1, last_wcc=0.9 * pos_tol)
    assert not wc.converged
    wc.update(LineData(1))
    assert wc.converged

def test_two_step(pos_tol, patch_max_move, patch_line_data):
    wc = WccConvergence(pos_tol=pos_tol)
    mv1 = pos_tol * 1.1
    mv2 = pos_tol * 0.9
    wc.update(LineData(mv1))
    wc.update(LineData(mv2))
    assert wc.max_move == mv2
    assert wc.converged
    assert wc.state == dict(max_move=mv2, last_wcc=mv2)

@pytest.fixture(params=[-1, 0, 1.2, 9])
def invalid_pos_tol(request):
    return request.param

def test_pos_tol_raise(invalid_pos_tol):
    with pytest.raises(ValueError):
        wc = WccConvergence(pos_tol=invalid_pos_tol)
