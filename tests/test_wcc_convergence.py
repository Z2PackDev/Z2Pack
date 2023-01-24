"""Test LineData controls implementing WCC convergence criteria."""
# pylint: disable=unused-argument,redefined-outer-name,unused-wildcard-import

import numpy as np
import pytest
import z2pack
from z2pack.line._control import PosCheck

from monkeypatch_data import *


def test_base(test_ctrl_base):
    test_ctrl_base(PosCheck)
    assert issubclass(PosCheck, z2pack._control.LineControl)  # pylint: disable=protected-access


# Monkeypatching s.t. the data.wcc is just a float, and _get_max_move is just min(wcc1, wcc2)
@pytest.fixture
def patch_line_max_move(monkeypatch):
    monkeypatch.setattr(
        z2pack.line._control, "_get_max_move", min  # pylint: disable=protected-access
    )


@pytest.fixture(params=np.linspace(0.01, 0.99, 21))
def pos_tol(request):
    return request.param


def test_one_step(pos_tol, patch_line_max_move):
    """
    Test that PosCheck does not converge with just a single step.
    """
    pos_check = PosCheck(pos_tol=pos_tol)
    pos_check.update(LineData(0.1))
    assert not pos_check.converged


def test_one_step_init(pos_tol, patch_line_max_move):
    """
    Test that PosCheck does not converge, if the state is manually set to corresond to one step.
    """
    pos_check = PosCheck(pos_tol=pos_tol)
    pos_check.state = dict(max_move=pos_tol * 1.1, last_wcc=0.9 * pos_tol)
    assert not pos_check.converged
    pos_check.update(LineData(1))
    assert pos_check.converged


def test_two_step(pos_tol, patch_line_max_move):
    """
    Test that PosCheck is converged after two steps, where the move is smaller than the tolerance.
    """
    pos_check = PosCheck(pos_tol=pos_tol)
    move_1 = pos_tol * 1.1
    move_2 = pos_tol * 0.9
    pos_check.update(LineData(move_1))
    pos_check.update(LineData(move_2))
    assert pos_check.max_move == move_2
    assert pos_check.converged
    assert pos_check.state == dict(max_move=move_2, last_wcc=move_2)


@pytest.fixture(params=[-1, 0, 1.2, 9])
def invalid_pos_tol(request):
    return request.param


def test_pos_tol_raise(invalid_pos_tol):
    """
    Test that a ValueError is raised if pos_tol is an invalid value.
    """
    with pytest.raises(ValueError):
        PosCheck(pos_tol=invalid_pos_tol)
