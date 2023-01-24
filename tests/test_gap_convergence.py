"""
Test GapCheck control.
"""
# pylint: disable=unused-wildcard-import,unused-argument,redefined-outer-name

import numpy as np
import pytest
from z2pack._control import SurfaceControl
from z2pack.surface._control import GapCheck

from monkeypatch_data import *


def test_base(test_ctrl_base):
    test_ctrl_base(GapCheck)
    assert issubclass(GapCheck, SurfaceControl)


@pytest.fixture(params=np.linspace(0.1, 0.49, 11))
def gap_tol(request):
    return request.param


@pytest.fixture(params=range(1, 10))
def num_lines(request):
    return request.param


def test_hit_gap(gap_tol, patch_surface_data):
    move_check = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 1], [0.5, 0.5]])
    move_check.update(data)
    assert move_check.converged == [False]


def test_trivial_wcc(gap_tol, num_lines, patch_surface_data):
    move_check = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 1]] * (num_lines + 1))
    move_check.update(data)
    assert move_check.converged == [True] * num_lines


def test_mixed_1(gap_tol, patch_surface_data):
    move_check = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 1], [0, 0.8]])
    move_check.update(data)
    assert move_check.converged == [gap_tol < 0.3]


def test_mixed_2(gap_tol, patch_surface_data):
    move_check = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 0.8], [0, 1]])
    move_check.update(data)
    assert move_check.converged == [gap_tol < 0.3]


def test_mixed_3(gap_tol, patch_surface_data):
    move_check = GapCheck(gap_tol=gap_tol)
    data = SurfaceData([[0, 0.8], [0, 0.2]])
    move_check.update(data)
    assert move_check.converged == [gap_tol * 0.8 < 0.2]
