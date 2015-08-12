#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 11:52:42 CEST
# File:    _core_utils.py

import copy

__all__ = ['_convcheck', '_sgng', '_gapfind', '_dist']

def _convcheck(list_a, list_b, epsilon):
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

    return max_move <= epsilon, max_move

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
    N = len(wcc)
    for i in range(0, N - 1):
        temp = wcc[i + 1] - wcc[i]
        if temp > gapsize:
            gapsize = temp
            gappos = i
    temp = wcc[0] - wcc[-1] + 1
    if temp > gapsize:
        gapsize = temp
        gappos = N - 1
    return (wcc[gappos] + gapsize / 2) % 1, gapsize

def _dist(x, y):
    """
    Returns the smallest distance on the periodic [0, 1) between x, y
    where x, y should be in [0, 1)
    """
    x = x % 1
    y = y % 1
    return min(abs(1 + x - y) % 1, abs(1 - x + y) % 1)
