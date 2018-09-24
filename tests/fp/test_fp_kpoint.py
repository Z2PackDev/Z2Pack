"""
Tests for kpoint functions.
"""
# pylint: disable=redefined-outer-name

import pytest
import numpy as np

import z2pack


@pytest.fixture
def kpt(line):
    """
    Return a list of k-points for a given 'line' fixture.
    """
    kpt = [np.array(line(tval)) for tval in np.linspace(0, 1, 11)]
    return kpt


STRAIGHT_SIMPLE = [
    lambda t, s1=s1, s2=s2: [s1, s2, t] for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
]
STRAIGHT_SIMPLE.extend([
    lambda t, s1=s1, s2=s2: [s1, t, s2] for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
])
STRAIGHT_SIMPLE.extend([
    lambda t, s1=s1, s2=s2: [t, s1, s2] for s1 in np.linspace(0, 1, 5)
    for s2 in np.linspace(0, 1, 5)
])

STRAIGHT_ANY_DIRECTION = [
    lambda t: [0, t, t], lambda t: [t, 0, t], lambda t: [0, 1 - t, 0],
    lambda t: [0.2, 0.2 + t, 0]
]

STRAIGHT_UNEQUAL_SPACING = [lambda t: [0, 0, t**2]]

STRAIGHT_MULTIPLE_BZ = [lambda t: [0, 0, 2 * t]]

NON_STRAIGHT = [
    lambda t: [0, np.cos(2 * np.pi * t), np.sin(2 * np.pi * t)],
    lambda t: [0, 0.2 * np.cos(2 * np.pi * t), 0.3 * np.sin(2 * np.pi * t)],
]

ALL_VALID = STRAIGHT_SIMPLE + STRAIGHT_ANY_DIRECTION + STRAIGHT_UNEQUAL_SPACING + STRAIGHT_MULTIPLE_BZ + NON_STRAIGHT

INVALID = [lambda t: [0, 0, 0.9 * t], lambda t: [0, t]]

ALL_LINES = ALL_VALID + INVALID

VALID_LINES = {
    z2pack.fp.kpoint.vasp.__name__: {
        'fct':
        z2pack.fp.kpoint.vasp,
        'valid':
        STRAIGHT_SIMPLE,
        'invalid':
        STRAIGHT_ANY_DIRECTION + STRAIGHT_UNEQUAL_SPACING +
        STRAIGHT_MULTIPLE_BZ + NON_STRAIGHT + INVALID
    },
    z2pack.fp.kpoint.qe.__name__: {
        'fct': z2pack.fp.kpoint.qe,
        'valid': ALL_VALID,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.qe_explicit.__name__: {
        'fct': z2pack.fp.kpoint.qe_explicit,
        'valid': ALL_VALID,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.abinit.__name__: {
        'fct': z2pack.fp.kpoint.abinit,
        'valid':
        STRAIGHT_SIMPLE + STRAIGHT_ANY_DIRECTION + STRAIGHT_MULTIPLE_BZ,
        'invalid': STRAIGHT_UNEQUAL_SPACING + NON_STRAIGHT + INVALID
    },
    z2pack.fp.kpoint.wannier90.__name__: {
        'fct': z2pack.fp.kpoint.wannier90,
        'valid': ALL_VALID,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.wannier90_nnkpts.__name__: {
        'fct': z2pack.fp.kpoint.wannier90_nnkpts,
        'valid': ALL_VALID,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.wannier90_full.__name__: {
        'fct': z2pack.fp.kpoint.wannier90_full,
        'valid': ALL_VALID,
        'invalid': INVALID
    }
}


@pytest.mark.parametrize('fct', sorted(VALID_LINES.keys()))
@pytest.mark.parametrize('line', ALL_LINES)
def test_lines(kpt, fct, line, compare_equal):
    """
    For each k-point function, test that it works for the lines it can handle, and raises ValueError for those it cannot.
    """
    if line in VALID_LINES[fct]['valid']:
        compare_equal(VALID_LINES[fct]['fct'](kpt))
    elif line in VALID_LINES[fct]['invalid']:
        with pytest.raises(ValueError):
            VALID_LINES[fct]['fct'](kpt)
    else:
        raise ValueError('missing test for this line and function')
