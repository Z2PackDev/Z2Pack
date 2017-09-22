"""
Test the function that computes the maximum move between two sets of WCC.
"""
# pylint: disable=redefined-outer-name

import copy
import random
random.seed(2512351)

import z2pack
max_move = z2pack._utils._get_max_move  # pylint: disable=protected-access,invalid-name

import pytest
import numpy as np


@pytest.fixture(params=range(2, 300, 3))
def num_wcc(request):
    return request.param


EPSILON = 1e-14


def test_zero(num_wcc):
    """
    Test that the maximum move is zero for two identical sets of WCC.
    """
    wcc_1 = [random.random() for _ in range(num_wcc)]
    assert max_move(wcc_1, wcc_1) == 0
    assert max_move(wcc_1, copy.deepcopy(wcc_1)) == 0


def test_single_move(num_wcc):
    """
    Test maximum move for a uniform shift on randomly distributed WCC.
    """
    wcc_1 = [random.random() for _ in range(num_wcc)]
    wcc_2 = copy.deepcopy(wcc_1)
    move = random.uniform(-1, 1) / num_wcc
    idx = random.randint(0, num_wcc - 1)
    wcc_2[idx] += move
    wcc_2[idx] %= 1
    assert max_move(wcc_1, wcc_2) <= abs(move) + EPSILON


def test_single_move_equal_spacing(num_wcc):
    """
    Test maximum move of a uniform shift on equally spaced WCC.
    """
    wcc_1 = list(np.linspace(0, 1, num_wcc, endpoint=False))
    wcc_2 = copy.deepcopy(wcc_1)
    move = random.uniform(-1, 1) / num_wcc
    idx = random.randint(0, num_wcc - 1)
    wcc_2[idx] += move
    wcc_2[idx] %= 1
    assert (
        abs(move) - EPSILON <= max_move(wcc_1, wcc_2) <= abs(move) + EPSILON
    )


def test_move_all(num_wcc):
    """
    Test a random move on all WCC.
    """
    wcc_1 = [random.random() for _ in range(num_wcc)]
    wcc_2 = copy.deepcopy(wcc_1)
    real_max_move = 0
    for idx in range(num_wcc):
        move = random.uniform(-1, 1) / (2 * num_wcc)
        real_max_move = max(abs(move), real_max_move)
        wcc_2[idx] += move
        wcc_2[idx] %= 1
    assert max_move(wcc_1, wcc_2) <= abs(real_max_move) + EPSILON
