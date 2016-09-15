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

straight_simple = [
    lambda t: [s1, s2, t]
    for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
]
straight_simple.extend([
    lambda t: [s1, t, s2]
    for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
])
straight_simple.extend([
    lambda t: [t, s1, s2]
    for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
])

straight_any_direction = [
    lambda t: [0, t, t], 
    lambda t: [t, 0, t],
    lambda t: [0, 1 - t, 0]
]

non_straight = [
    lambda t: [0, 0, t**2],
    lambda t: [0, 0, 2 * t],
    lambda t: [0, np.cos(2 * np.pi * t), np.sin(2 * np.pi * t)],
    lambda t: [0, 0.2 * np.cos(2 * np.pi * t), 0.3 * np.sin(2 * np.pi * t)],
]

invalid = [
    lambda t: [0, 0, 0.9 * t]
]

ALL_LINES = straight_simple + straight_any_direction + non_straight + invalid

VALID_LINES = {
    z2pack.fp.kpoint.vasp.__name__: {'fct': z2pack.fp.kpoint.vasp, 'valid': straight_simple, 'invalid': straight_any_direction + non_straight + invalid},
    z2pack.fp.kpoint.qe.__name__: {'fct': z2pack.fp.kpoint.qe, 'valid': straight_simple + straight_any_direction + non_straight, 'invalid': invalid}
}


@pytest.mark.parametrize('fct', sorted(VALID_LINES.keys()))
@pytest.mark.parametrize('line', ALL_LINES)
def test_valid_lines(kpt, fct, line, compare_equal):
    if line in VALID_LINES[fct]['valid']:
        compare_equal(VALID_LINES[fct]['fct'](kpt))
    elif line in VALID_LINES[fct]['invalid']:
        with pytest.raises(ValueError):
            VALID_LINES[fct]['fct'](kpt)
    else:
        raise ValueError('missing test for this line and function')
