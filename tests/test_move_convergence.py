"""Test MoveCheck convergence test."""
# pylint: disable=unused-argument,unused-wildcard-import,redefined-outer-name

from monkeypatch_data import *

import z2pack
from z2pack._control import SurfaceControl
from z2pack.surface._control import MoveCheck
import pytest
import numpy as np


def test_base(test_ctrl_base):
    test_ctrl_base(MoveCheck)
    assert issubclass(MoveCheck, SurfaceControl)


@pytest.fixture(params=np.linspace(0.1, 0.5, 11))
def move_tol(request):
    return request.param


def test_single_update(move_tol, patch_max_move, patch_surface_data):
    """
    Test move convergence check with a simple WCC progression.
    """
    move_check = MoveCheck(move_tol=move_tol)
    vals = [0.1, 0.2, 0.3, 0.4]
    move_check.update(SurfaceData([[v] for v in vals]))
    conv = [min(v1, v2) < move_tol for v1, v2 in zip(vals[:-1], vals[1:])]
    assert move_check.converged == conv
