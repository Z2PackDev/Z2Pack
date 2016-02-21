#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.02.2016 10:10:06 MST
# File:    test_move_convergence.py

from z2pack._core.surface._control import GapConvergence
from z2pack._core._control_base import SurfaceControl
from z2pack._core._result import Result
from z2pack._core.surface._data import SurfaceData
from z2pack._core.line._data import LineData

import z2pack
import pytest
import numpy as np

def test_base(test_ctrl_base):
    test_ctrl_base(GapConvergence)
    assert issubclass(GapConvergence, SurfaceControl)

@pytest.fixture
def patch_line_data(monkeypatch):
    def init(self, wcc):
        self._wcc = wcc

    monkeypatch.setattr(LineData, '__init__', init)

@pytest.fixture
def get_surface_data(patch_line_data):
    def inner(wcc_list):
        t = np.linspace(0, 1, len(wcc_list))
        data = SurfaceData()
        for tval, wcc in zip(t, wcc_list):
            data.add_line(tval, Result(LineData(wcc), []))
        return data
    return inner

@pytest.fixture(params=np.linspace(0.1, 0.49, 11))
def gap_tol(request):
    return request.param

@pytest.fixture(params=range(1, 10))
def N(request):
    return request.param

def test_hit_gap(gap_tol, get_surface_data):
    mc = GapConvergence(gap_tol=gap_tol)
    data = get_surface_data([[0, 1], [0.5, 0.5]])
    mc.update(data)
    assert mc.converged == [False]
    
def test_trivial_wcc(gap_tol, N, get_surface_data):
    mc = GapConvergence(gap_tol=gap_tol)
    data = get_surface_data([[0, 1]] * (N + 1))
    mc.update(data)
    assert mc.converged == [True] * N
    
def test_mixed_1(gap_tol, get_surface_data):
    mc = GapConvergence(gap_tol=gap_tol)
    data = get_surface_data([[0, 1], [0, 0.8]])
    mc.update(data)
    assert mc.converged == (gap_tol < 0.3)

def test_mixed_2(gap_tol, get_surface_data):
    mc = GapConvergence(gap_tol=gap_tol)
    data = get_surface_data([[0, 0.8], [0, 1]])
    mc.update(data)
    assert mc.converged == (gap_tol < 0.3)
