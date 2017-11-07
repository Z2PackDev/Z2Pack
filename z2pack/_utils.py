"""Utilities for calculating properties of Wannier charge center lists."""

import copy

__all__ = ['_get_max_move', '_sgng', '_gapfind', '_dist']


def _get_max_move(list_a, list_b):
    """
    new style convergence check!!
    """
    full_list = copy.deepcopy(list_a)
    full_list.extend(list_b)
    gap = _gapfind(full_list)[0]
    a_mod = sorted([(x + 1 - gap) % 1 for x in list_a])
    b_mod = sorted([(x + 1 - gap) % 1 for x in list_b])
    max_move = 0.
    for a_pos, b_pos in zip(a_mod, b_mod):
        max_move = max(_dist(a_pos, b_pos), max_move)

    return max_move


def _sgng(z, zplus, x):
    """
    calculates the invariant between two WCC strings
    """
    return -1 if (max(zplus, z) > x and min(zplus, z) < x) else 1


def _gapfind(wcc):
    """
    finds the largest gap in vector wcc, modulo 1
    """
    wcc = sorted(wcc)
    gapsize = 0
    gappos = 0
    num_wcc = len(wcc)
    for i, (wcc_left, wcc_right) in enumerate(zip(wcc, wcc[1:])):
        temp = wcc_right - wcc_left
        if temp > gapsize:
            gapsize = temp
            gappos = i
    # this needs to be explicit, otherwise gapsize == 1 is not possible
    temp = wcc[0] - wcc[-1] + 1
    if temp > gapsize:
        gapsize = temp
        gappos = num_wcc - 1
    return (wcc[gappos] + gapsize / 2) % 1, gapsize


def _dist(x, y):
    """
    Returns the smallest distance on the periodic [0, 1) between x, y
    where x, y should be in [0, 1)
    """
    x %= 1
    y %= 1
    return min((x - y) % 1, (y - x) % 1)


def _pol_step(pol_list):
    """
    Returns the value of the minimal change in each step for a list of polarization values.
    """
    offset = [-1, 0, 1]
    pol_list = [p % 1 for p in pol_list]
    res = []
    for pol_left, pol_right in zip(pol_list[:-1], pol_list[1:]):
        res.append(min((pol_right - pol_left + o for o in offset), key=abs))
    return res
