"""Test the function that computes the Chern invariant."""
# pylint: disable=unused-argument,redefined-outer-name,unused-wildcard-import

import random

import pytest

from monkeypatch_data import *
import z2pack


@pytest.fixture(params=range(6))
def num_lines(request):
    return request.param


@pytest.fixture(params=range(2, 5))
def num_lines_nonzero(request):
    return request.param


@pytest.fixture(params=range(1, 6))
def num_wcc(request):
    return request.param


@pytest.fixture(params=range(-3, 3))
def offset(request):
    return request.param


@pytest.fixture(params=np.linspace(0.05, 0.95, 10))
def x(request):
    return request.param


def test_trivial(num_lines, num_wcc, patch_surface_data):
    """Test straight WCC lines"""
    wcc = [np.linspace(0, 1, num_wcc) for j in range(num_lines)]
    data = SurfaceData(wcc)
    assert z2pack.invariant.chern(data) == 0


def test_linear(num_lines_nonzero, x, offset, patch_surface_data):
    """Test a linear offset"""
    wcc = np.array([np.linspace(x, offset + x, num_lines_nonzero)]).T
    data = SurfaceData(wcc)
    assert (abs(offset) / (num_lines_nonzero - 1) >= 0.5) or np.isclose(
        z2pack.invariant.chern(data), offset
    )


def test_linear_2(num_lines_nonzero, num_wcc, x, offset, patch_surface_data):
    """
    Test a linear offset, with some additional lines in between
    """
    wcc = [np.linspace(x, offset + x, num_lines_nonzero)]
    wcc += [[random.random()] * num_lines_nonzero] * num_wcc
    wcc = np.array(wcc).T
    data = SurfaceData(wcc)
    assert (abs(offset) / (num_lines_nonzero - 1) >= 0.5) or np.isclose(
        z2pack.invariant.chern(data), offset
    )
