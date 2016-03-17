#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.03.2016 14:38:55 CET
# File:    invariant.py

from .._utils import _pol_step, _sgng

def chern(surface_result):
    r"""
    Computes the Chern number corresponding to some surface.

    :param surface_result: Result of a WCC calculation on a Surface.
    :type surface_result: SurfaceResult or SurfaceData
    """
    return sum(_pol_step(surface_result.pol))

def z2(surface_result):
    r"""
    Computes the Z2 invariant corresponding to some surface.

    :param surface_result: Result of a WCC calculation on a Surface.
    :type surface_result: SurfaceResult or SurfaceData
    """
    wcc = surface_result.wcc
    gap = surface_result.gap_pos
    inv = 1
    for i in range(0, len(wcc) - 1):
        for j in range(len(wcc[0])):
            inv *= _sgng(
                gap[i],
                gap[i + 1],
                wcc[i + 1][j]
            )
    return 1 if inv == -1 else 0
