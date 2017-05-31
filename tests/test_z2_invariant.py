#!/usr/bin/env python
# -*- coding: utf-8 -*-

import z2pack
import random

import pytest

from monkeypatch_data import *

@pytest.fixture(params=range(10))
def N(request):
    return request.param

@pytest.fixture(params=range(1, 20))
def M(request):
    return request.param

@pytest.fixture(params=range(4, 20))
def L(request):
    return request.param

@pytest.fixture(params=np.linspace(0.05, 0.95, 10))
def x(request):
    return request.param

def test_trivial(N, M, patch_surface_data):
    wcc = [np.linspace(0, 1, M) for j in range(N)]
    data = SurfaceData(wcc)
    assert z2pack.invariant.z2(data) == 0

def test_linear(L, x, patch_surface_data):
    wcc = np.array([np.linspace(0, x, L), np.linspace(1, x, L)]).T
    data = SurfaceData(wcc)
    assert z2pack.invariant.z2(data) == 1

def test_linear_2(M, L, patch_surface_data):
    wcc = list(zip(np.linspace(0, 0.6, L), np.linspace(1, 0.6, L)))
    rand = list(sorted([random.random() for _ in range(M)] * 2))
    wcc += [rand] * L
    wcc = np.array(wcc)
    data = SurfaceData(wcc)
    assert z2pack.invariant.z2(data) == 1
