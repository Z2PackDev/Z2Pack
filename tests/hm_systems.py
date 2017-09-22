#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

import z2pack


class OverlapMockSystem(z2pack.system.OverlapSystem):
    def __init__(self, eigenstate_system):
        self.eigenstate_system = eigenstate_system

    def get_mmn(self, kpt):
        return [
            z2pack.line.
            EigenstateLineData(self.eigenstate_system.get_eig(kpt)).wilson
        ]


@pytest.fixture(params=np.linspace(-1, 1, 11))
def kz(request):
    return request.param


@pytest.fixture(params=[10**n for n in range(-4, -1)])
def pos_tol(request):
    return request.param


@pytest.fixture(params=[False, True])
def simple_system(request):
    res = z2pack.hm.System(lambda k: np.eye(4))
    if request.param:
        res = OverlapMockSystem(res)
    return res


@pytest.fixture
def simple_line():
    return lambda t: [0, 0, 0]


@pytest.fixture
def simple_surface():
    return lambda s, t: [0, 0, 0]


@pytest.fixture(params=[False, True])
def weyl_system(request):
    res = z2pack.hm.System(
        lambda k: np.array(
            [
                [k[2], k[0] -1j * k[1]],
                [k[0] + 1j * k[1], -k[2]]
            ]
        )
    )
    if request.param:
        res = OverlapMockSystem(res)
    return res


@pytest.fixture
def weyl_line(kz):
    return lambda t: [np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), kz]


@pytest.fixture
def weyl_surface():
    return z2pack.shape.Sphere([0, 0, 0], 1.)
