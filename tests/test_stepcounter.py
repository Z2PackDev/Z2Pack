#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.02.2016 18:14:05 MST
# File:    test_stepcounter.py

from z2pack.line._control import StepCounter
import z2pack

import pytest

def test_base(test_ctrl_base):
    test_ctrl_base(StepCounter)
    assert issubclass(StepCounter, z2pack._control.LineControl)

@pytest.fixture(params=list(range(1, 20)))
def N1(request):
    return request.param

@pytest.fixture(params=list(range(1, 20)))
def N2(request):
    return request.param


def test_step(N1):
    sc = StepCounter(iterator=range(0, 100, 2))
    for _ in range(N1):
        n = next(sc)['num_steps']
        assert sc.state == n
    assert n == 2 * N1

def test_nonzero_start(N1, N2):
    sc = StepCounter(iterator=range(0, 1000, 3))
    sc.state = N2
    assert sc.state == N2
    for _ in range(N1):
        n = next(sc)['num_steps']
        assert sc.state == n
    assert n == 3 * (N1 + int(N2 / 3))

def test_stopiteration(N1):
    sc = StepCounter(iterator=range(0, 3 * N1, 2))
    with pytest.raises(StopIteration):
        while True:
            n = next(sc)['num_steps']
            assert sc.state == n
    assert n == int((3 * N1 - 1) / 2) * 2
