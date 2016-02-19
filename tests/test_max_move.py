#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 15:23:55 MST
# File:    test_max_move.py

import z2pack
max_move = z2pack._core._utils._get_max_move

import copy
import pytest
import random
import numpy as np

@pytest.fixture(params=range(2, 100, 3))
def N(request):
    return request.param

@pytest.fixture
def l1(N):
    return []

def test_zero(N):
    l1 = [random.random() for _ in range(N)]
    assert max_move(l1, l1) == 0
    assert max_move(l1, copy.deepcopy(l1)) == 0

def test_single_move(N):
    l1 = [random.random() for _ in range(N)]
    l2 = copy.deepcopy(l1)
    move = random.uniform(-1, 1) / N
    idx = random.randint(0, N - 1)
    l2[idx] += move
    l2[idx] %= 1
    assert(max_move(l1, l2) <= abs(move) + 1e-14)

def test_single_move_equal_spacing(N):
    l1 = list(np.linspace(0, 1, N, endpoint = False))
    l2 = copy.deepcopy(l1)
    move = random.uniform(-1, 1) / N
    idx = random.randint(0, N - 1)
    l2[idx] += move
    l2[idx] %= 1
    assert(abs(move) - 1e-14 <= max_move(l1, l2) <= abs(move) + 1e-14)
