#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.02.2016 10:10:06 MST
# File:    test_move_convergence.py

import pytest
import numpy as np

import z2pack
from z2pack.surface._control import GapCheck
from z2pack._control import SurfaceControl

from monkeypatch_data import *

def test_base(test_ctrl_base):
    test_ctrl_base(GapCheck)
    assert issubclass(GapCheck, SurfaceControl)

@pytest.fixture(params=np.linspace(0.1, 0.49, 11))
def gap_tol(request):
    return request.param

@pytest.fixture(params=range(1, 10))
def N(request):
    return request.param

def test_hit_gap(gap_tol, patch_surface_data):
    mc = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 1], [0.5, 0.5]])
    mc.update(data)
    assert mc.converged == [False]
    
def test_trivial_wcc(gap_tol, N, patch_surface_data):
    mc = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 1]] * (N + 1))
    mc.update(data)
    assert mc.converged == [True] * N
    
def test_mixed_1(gap_tol, patch_surface_data):
    mc = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 1], [0, 0.8]])
    mc.update(data)
    assert mc.converged == (gap_tol < 0.3)

def test_mixed_2(gap_tol, patch_surface_data):
    mc = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 0.8], [0, 1]])
    mc.update(data)
    assert mc.converged == (gap_tol < 0.3)
