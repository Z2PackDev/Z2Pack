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
    kpt = [
        np.array(line(tval))
        for tval in [0., 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.]
    ]
    return kpt


VALS = [0., 0.25, 0.5, 0.75, 1.]

STRAIGHT_SIMPLE = [
    lambda t, s1=s1, s2=s2: [s1, s2, t] for s1 in VALS for s2 in VALS
]
STRAIGHT_SIMPLE.extend([
    lambda t, s1=s1, s2=s2: [s1, t, s2] for s1 in VALS for s2 in VALS
])
STRAIGHT_SIMPLE.extend([
    lambda t, s1=s1, s2=s2: [t, s1, s2] for s1 in VALS for s2 in VALS
])

STRAIGHT_ANY_DIRECTION = [
    lambda t: [0, t, t], lambda t: [t, 0, t], lambda t: [0, 1 - t, 0],
    lambda t: [0.2, 0.2 + t, 0]
]

STRAIGHT_UNEQUAL_SPACING = [lambda t: [0, 0, t**2]]

STRAIGHT_MULTIPLE_BZ = [lambda t: [0, 0, 2 * t]]

NON_STRAIGHT = [
    lambda t: [0, np.cos(2 * np.pi * t),
               np.sin(2 * np.pi * t)],
    lambda t: [0, 0.2 * np.cos(2 * np.pi * t), 0.3 * np.sin(2 * np.pi * t)],
]

VALID_COMPARABLE = STRAIGHT_SIMPLE + STRAIGHT_ANY_DIRECTION + STRAIGHT_UNEQUAL_SPACING + STRAIGHT_MULTIPLE_BZ

VALID_INCOMPARABLE = NON_STRAIGHT

ALL_VALID = VALID_COMPARABLE + VALID_INCOMPARABLE

INVALID = [lambda t: [0, 0, 0.9 * t], lambda t: [0, t]]

ALL_LINES = ALL_VALID + INVALID

VALID_LINES = {
        z2pack.fp.kpoint.elk.__name__: {
        'fct':
        z2pack.fp.kpoint.elk,
        'valid_comparable':
        STRAIGHT_SIMPLE,
        'valid_incomparable': [],
        'invalid':
        STRAIGHT_ANY_DIRECTION + STRAIGHT_UNEQUAL_SPACING +
        STRAIGHT_MULTIPLE_BZ + NON_STRAIGHT + INVALID
    },
    z2pack.fp.kpoint.vasp.__name__: {
        'fct':
        z2pack.fp.kpoint.vasp,
        'valid_comparable':
        STRAIGHT_SIMPLE,
        'valid_incomparable': [],
        'invalid':
        STRAIGHT_ANY_DIRECTION + STRAIGHT_UNEQUAL_SPACING +
        STRAIGHT_MULTIPLE_BZ + NON_STRAIGHT + INVALID
    },
    z2pack.fp.kpoint.qe.__name__: {
        'fct': z2pack.fp.kpoint.qe,
        'valid_comparable': VALID_COMPARABLE,
        'valid_incomparable': VALID_INCOMPARABLE,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.qe_explicit.__name__: {
        'fct': z2pack.fp.kpoint.qe_explicit,
        'valid_comparable': VALID_COMPARABLE,
        'valid_incomparable': VALID_INCOMPARABLE,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.abinit.__name__: {
        'fct': z2pack.fp.kpoint.abinit,
        'valid_comparable':
        STRAIGHT_SIMPLE + STRAIGHT_ANY_DIRECTION + STRAIGHT_MULTIPLE_BZ,
        'valid_incomparable': [],
        'invalid': STRAIGHT_UNEQUAL_SPACING + NON_STRAIGHT + INVALID
    },
    z2pack.fp.kpoint.wannier90.__name__: {
        'fct': z2pack.fp.kpoint.wannier90,
        'valid_comparable': VALID_COMPARABLE,
        'valid_incomparable': VALID_INCOMPARABLE,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.wannier90_nnkpts.__name__: {
        'fct': z2pack.fp.kpoint.wannier90_nnkpts,
        'valid_comparable': VALID_COMPARABLE,
        'valid_incomparable': VALID_INCOMPARABLE,
        'invalid': INVALID
    },
    z2pack.fp.kpoint.wannier90_full.__name__: {
        'fct': z2pack.fp.kpoint.wannier90_full,
        'valid_comparable': VALID_COMPARABLE,
        'valid_incomparable': VALID_INCOMPARABLE,
        'invalid': INVALID
    }
}


@pytest.mark.parametrize('fct', sorted(VALID_LINES.keys()))
@pytest.mark.parametrize('line', ALL_LINES)
def test_lines(kpt, fct, line, compare_equal):
    """
    For each k-point function, test that it works for the lines it can handle, and raises ValueError for those it cannot.
    """
    line_mapping = VALID_LINES[fct]
    if line in line_mapping['valid_comparable']:
        compare_equal(VALID_LINES[fct]['fct'](kpt))
    elif line in line_mapping['valid_incomparable']:
        VALID_LINES[fct]['fct'](kpt)
    elif line in line_mapping['invalid']:
        with pytest.raises(ValueError):
            line_mapping['fct'](kpt)
    else:
        raise ValueError('missing test for this line and function')
