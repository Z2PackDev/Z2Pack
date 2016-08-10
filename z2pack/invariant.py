#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.03.2016 14:38:55 CET
# File:    invariant.py

from fsc.export import export

from ._utils import _pol_step, _sgng

@export
def chern(surface_result):
    r"""
    Computes the Chern number corresponding to some surface.

    :param surface_result: Result of a WCC calculation on a Surface.
    :type surface_result: SurfaceResult or SurfaceData
    """
    return sum(_pol_step(surface_result.pol))

@export
def z2(surface_result):
    r"""
    Computes the Z2 invariant corresponding to some surface.

    :param surface_result: Result of a WCC calculation on a Surface.
    :type surface_result: SurfaceResult or SurfaceData
    """
    wcc = surface_result.wcc
    gap = surface_result.gap_pos
    inv = 1
    for g1, g2, w2 in zip(gap, gap[1:], wcc[1:]):
        for w in w2:
            inv *= _sgng(g1, g2, w)
    return 1 if inv == -1 else 0
