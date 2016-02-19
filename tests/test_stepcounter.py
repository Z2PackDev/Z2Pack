#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.02.2016 18:14:05 MST
# File:    test_stepcounter.py

import sys
import pytest
from z2pack._core.line._control import StepCounter

@pytest.fixture
def N(request, params=list(range(20))):
    return request.param


def test_step():
    sc = StepCounter(range(0, 100, 2))
    for _ in range(N):
        n = next(sc)
    assert n == 2 * N

def test_state(N):
    pass
