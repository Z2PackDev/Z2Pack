#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    26.03.2016 22:56:57 CET
# File:    test_fp_kpoint.py

import pytest
import numpy as np

import z2pack

@pytest.fixture(params=np.linspace(0, 1, 11))
def kpt(request, line):
    kpt = [np.array(line(tval)) for tval in np.linspace(0, 1, 11)]
    return kpt

valid_lines = [
    lambda t: [s1, s2, t]
    for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
]
valid_lines.extend([
    lambda t: [s1, t, s2]
    for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
])
valid_lines.extend([
    lambda t: [t, s1, s2]
    for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
])

@pytest.mark.parametrize('line', valid_lines)
def test_valid_surface(kpt, compare_equal):
    compare_equal(z2pack.fp.kpoint.vasp(kpt))
