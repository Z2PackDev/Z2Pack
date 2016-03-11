#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    11.03.2016 11:24:24 CET
# File:    test_z2_invariant.py

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
    wcc = [np.linspace(0, 1, M) for j in range(N)]
    data = SurfaceData(wcc)
    assert z2pack.surface.invariant.chern(data) == 0

def test_linear(L, x, patch_surface_data):
    wcc = np.array([np.linspace(x,  1 + x, L)]).T
    data = SurfaceData(wcc)
    assert np.isclose(z2pack.surface.invariant.chern(data), 1)

def test_linear_2(L, x, offset, patch_surface_data):
    wcc = np.array([np.linspace(x,  offset + x, L)]).T
    data = SurfaceData(wcc)
    assert (abs(offset) / (L - 1) >= 0.5) or np.isclose(z2pack.surface.invariant.chern(data), offset)

def test_linear_3(M, L, x, offset, patch_surface_data):
    wcc = [np.linspace(x,  offset + x, L)]
    wcc += [[random.random()] * L] * M
    wcc = np.array(wcc).T
    #~ wcc = list(zip(np.linspace(0, 0.6, L), np.linspace(1, 0.6, L)))
    #~ rand = list(sorted([random.random() for _ in range(M)]))
    #~ wcc += [rand] * L
    #~ wcc = np.array(wcc)
    data = SurfaceData(wcc)
    assert (abs(offset) / (L - 1) >= 0.5) or np.isclose(z2pack.surface.invariant.chern(data), offset)
