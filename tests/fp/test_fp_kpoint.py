#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

import z2pack

@pytest.fixture
def kpt(line):
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
    lambda t: [0, 1 - t, 0],
    lambda t: [0.2, 0.2 + t, 0]
]

straight_unequal_spacing = [
    lambda t: [0, 0, t**2]
]

straight_multiple_bz = [
    lambda t: [0, 0, 2 * t]
]

non_straight = [
    lambda t: [0, np.cos(2 * np.pi * t), np.sin(2 * np.pi * t)],
    lambda t: [0, 0.2 * np.cos(2 * np.pi * t), 0.3 * np.sin(2 * np.pi * t)],
]

all_valid = straight_simple + straight_any_direction + straight_unequal_spacing + straight_multiple_bz + non_straight

invalid = [
    lambda t: [0, 0, 0.9 * t],
    lambda t: [0, t]
]

ALL_LINES = all_valid + invalid

VALID_LINES = {
    z2pack.fp.kpoint.vasp.__name__: {'fct': z2pack.fp.kpoint.vasp, 'valid': straight_simple, 'invalid': straight_any_direction + straight_unequal_spacing + straight_multiple_bz + non_straight + invalid},
    z2pack.fp.kpoint.qe.__name__: {'fct': z2pack.fp.kpoint.qe, 'valid': all_valid, 'invalid': invalid},
    z2pack.fp.kpoint.qe_explicit.__name__: {'fct': z2pack.fp.kpoint.qe_explicit, 'valid': all_valid, 'invalid': invalid},
    z2pack.fp.kpoint.abinit.__name__: {'fct': z2pack.fp.kpoint.abinit, 'valid': straight_simple + straight_any_direction + straight_multiple_bz, 'invalid': straight_unequal_spacing + non_straight + invalid},
    z2pack.fp.kpoint.wannier90.__name__: {'fct': z2pack.fp.kpoint.wannier90, 'valid': all_valid, 'invalid': invalid},
    z2pack.fp.kpoint.wannier90_nnkpts.__name__: {'fct': z2pack.fp.kpoint.wannier90_nnkpts, 'valid': all_valid, 'invalid': invalid},
    z2pack.fp.kpoint.wannier90_full.__name__: {'fct': z2pack.fp.kpoint.wannier90_full, 'valid': all_valid, 'invalid': invalid}
}


@pytest.mark.parametrize('fct', sorted(VALID_LINES.keys()))
@pytest.mark.parametrize('line', ALL_LINES)
def test_lines(kpt, fct, line, compare_equal):
    if line in VALID_LINES[fct]['valid']:
        compare_equal(VALID_LINES[fct]['fct'](kpt))
    elif line in VALID_LINES[fct]['invalid']:
        with pytest.raises(ValueError):
            VALID_LINES[fct]['fct'](kpt)
    else:
        raise ValueError('missing test for this line and function')
