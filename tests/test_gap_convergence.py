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

#~ from monkeypatch_surface import *

import z2pack
import pytest
import numpy as np

def test_base(test_ctrl_base):
    test_ctrl_base(GapConvergence)
    assert issubclass(GapConvergence, SurfaceControl)

@pytest.fixture(params=np.linspace(0.1, 0.5, 11))
def gap_tol(request):
    return request.param


def test_single_update(move_tol, patch_max_move):
    mc = GapConvergence(gap_tol=gap_tol)
    vals = [0.1, 0.2, 0.3, 0.4]
    mc.update(TrivialSurfaceData(vals))
    conv = [min(v1, v2) < move_tol for v1, v2 in zip(vals[:-1], vals[1:])]
    assert mc.converged == conv
