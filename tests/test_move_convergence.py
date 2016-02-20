#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.02.2016 09:47:28 MST
# File:    test_move_control.py

from z2pack._core.surface._control import MoveConvergence

import z2pack
import pytest
import numpy as np

@pytest.fixture(params=np.linspace(0.1, 0.5, 11))
def move_tol(request):
    return request.param

@pytest.fixture
def patch_max_move(monkeypatch):
    monkeypatch.setattr(z2pack._core.surface._control, '_get_max_move', min)

class TrivialLineData:
    def __init__(self, val):
        self.wcc = val

class TrivialLineResult:
    def __init__(self, val):
        self.data = TrivialLineData(val)

class TrivialSurfaceLine:
    def __init__(self, val):
        self.result = TrivialLineResult(val)

class TrivialSurfaceData:
    def __init__(self, vals):
        self.lines = [TrivialSurfaceLine(val) for val in vals]

def test_single_update(move_tol, patch_max_move):
    mc = MoveConvergence(move_tol=move_tol)
    vals = [0.1, 0.2, 0.3, 0.4]
    mc.update(TrivialSurfaceData(vals))
    conv = [min(v1, v2) < move_tol for v1, v2 in zip(vals[:-1], vals[1:])]
    assert mc.converged == conv
