#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 14:40:53 MST
# File:    test_line_run.py

import inspect

import pytest
import numpy as np

import z2pack

@pytest.fixture(params=np.linspace(-1, 1, 11))
def kz(request):
    return request.param

def test_trivial_run(compare_equal):
    sys = z2pack.em.System(lambda k: np.eye(4))
    line = lambda k: [0, 0, 0]
    result = z2pack.line.run(system=sys, line=line)
    assert result.wcc == [0, 0]
    assert result.gap_pos == 0.5
    assert result.gap_size == 1
    assert result.ctrl_states[z2pack._core.line._control.StepCounter] == 10
    assert result.ctrl_states[z2pack._core.line._control.WccConvergence] == dict(max_move=0, last_wcc=[0, 0])
    
def test_weyl(kz, compare_data):
    sys = z2pack.em.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    line = lambda t: [np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), kz]
    result = z2pack.line.run(system=sys, line=line)
    compare_data(np.isclose, result.wcc)
