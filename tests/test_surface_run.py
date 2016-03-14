#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.03.2016 10:29:04 CET
# File:    test_surface_run.py

import pytest

import numpy as np

import z2pack

@pytest.fixture(params=range(5, 11, 2))
def num_strings(request):
    return request.param

@pytest.fixture(params=np.linspace(0.1, 0.4, 5))
def move_tol(request):
    return request.param

@pytest.fixture(params=[10**n for n in range(-5, -2)])
def pos_tol(request):
    return request.param

@pytest.fixture(params=[10**n for n in range(-4, -1)])
def gap_tol(request):
    return request.param


def test_simple(num_strings):
    system = z2pack.em.System(lambda k: np.eye(4))
    surface = lambda s, t: [0, 0, 0]
    result = z2pack.surface.run(system=system, surface=surface, num_strings=num_strings)
    assert result.wcc == [[0, 0]] * num_strings
    assert result.gap_size == [1] * num_strings
    assert result.gap_pos == [0.5] * num_strings
    assert result.ctrl_states == {}

def test_weyl(compare_data, pos_tol, gap_tol, move_tol, num_strings):
    system = z2pack.em.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    result = z2pack.surface.run(
        system=system,
        surface=z2pack.shapes.Sphere([0, 0, 0], 1.),
        num_strings=num_strings,
        move_tol=move_tol,
        gap_tol=gap_tol,
        pos_tol=pos_tol
    )
    compare_data(lambda l1, l2: all(np.isclose(x1, x2) for x1, x2 in zip(l1, l2)) and len(l1) == len(l2), result.wcc)
