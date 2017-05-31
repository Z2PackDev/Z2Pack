#!/usr/bin/env python
# -*- coding: utf-8 -*-

import z2pack
import random

import pytest

from monkeypatch_data import *

@pytest.fixture(params=range(10))
def N(request):
    return request.param

@pytest.fixture(params=range(1, 10))
def M(request):
    return request.param

@pytest.fixture(params=range(4, 10))
def L(request):
    return request.param

@pytest.fixture(params=range(-3, 3))
def offset(request):
    return request.param

@pytest.fixture(params=np.linspace(0.05, 0.95, 10))
def x(request):
    return request.param

def test_trivial(N, M, patch_surface_data):
    """Test straight WCC lines"""
    wcc = [np.linspace(0, 1, M) for j in range(N)]
    data = SurfaceData(wcc)
    assert z2pack.invariant.chern(data) == 0

def test_linear(L, x, offset, patch_surface_data):
    """Test a linear offset"""
    wcc = np.array([np.linspace(x,  offset + x, L)]).T
    data = SurfaceData(wcc)
    assert (abs(offset) / (L - 1) >= 0.5) or np.isclose(z2pack.invariant.chern(data), offset)

def test_linear_2(M, L, x, offset, patch_surface_data):
    """Test a linear offset, with some additional lines in between"""
    wcc = [np.linspace(x,  offset + x, L)]
    wcc += [[random.random()] * L] * M
    wcc = np.array(wcc).T
    data = SurfaceData(wcc)
    assert (abs(offset) / (L - 1) >= 0.5) or np.isclose(z2pack.invariant.chern(data), offset)
