"""Tests for the function that computes the Z2 invariant."""
# pylint: disable=unused-argument,redefined-outer-name

import random

import pytest
import z2pack

from monkeypatch_data import *  # pylint: disable=unused-wildcard-import


@pytest.fixture(params=range(10))
def num_lines(request):
    return request.param


@pytest.fixture(params=range(1, 20))
def num_wcc(request):
    return request.param


@pytest.fixture(params=range(4, 20))
def num_lines_nonzero(request):
    return request.param


@pytest.fixture(params=np.linspace(0.05, 0.95, 10))
def x(request):
    return request.param


def test_trivial(num_lines, num_wcc, patch_surface_data):
    """
    Test Z2=0 with equally spaced WCC.
    """
    wcc = [np.linspace(0, 1, num_wcc) for j in range(num_lines)]
    data = SurfaceData(wcc)
    assert z2pack.invariant.z2(data, check_kramers_pairs=False) == 0


def test_not_even_number_wcc(N, M, patch_surface_data):  # pylint: disable=invalid-name
    """
    Test that the Kramers pairs check raises when an odd number of WCC is present.
    """
    wcc = [np.linspace(0, 1, 2 * M + 1) for j in range(N + 1)]
    data = SurfaceData(wcc)
    with pytest.raises(ValueError):
        z2pack.invariant.z2(data)


def test_not_kramers_pairs(patch_surface_data):
    """
    Test that the check for Kramers pairs raises when WCC are not pairs.
    """
    data = SurfaceData([[0., 0.], [0.5, 0.6]])
    with pytest.raises(ValueError):
        print(z2pack.invariant.z2(data))


def test_linear(num_lines_nonzero, x, patch_surface_data):
    """
    Test non-zero Z2 invariant with linear WCC evolution.
    """
    wcc = np.array([
        np.linspace(0, x, num_lines_nonzero),
        np.linspace(1, x, num_lines_nonzero)
    ]).T
    data = SurfaceData(wcc)
    assert z2pack.invariant.z2(data) == 1


def test_linear_2(num_wcc, num_lines_nonzero, patch_surface_data):
    """
    Test non-zero Z2 invariant with linear WCC evolution, and added random WCC.
    """
    wcc = list(
        zip(
            np.linspace(0, 0.6, num_lines_nonzero),
            np.linspace(1, 0.6, num_lines_nonzero)
        )
    )
    rand = list(sorted([random.random() for _ in range(num_wcc)] * 2))
    wcc += [rand] * num_lines_nonzero
    wcc = np.array(wcc)
    data = SurfaceData(wcc)
    assert z2pack.invariant.z2(data) == 1
