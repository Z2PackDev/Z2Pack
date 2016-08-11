#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.03.2016 14:38:55 CET
# File:    invariant.py

"""
This submodule contains functions for calculating the topological invariants from the result of a WCC / Wilson loop calculation.
"""

from fsc.export import export

from ._utils import _pol_step, _sgng

@export
def chern(surface_result):
    r"""
    Computes the Chern number corresponding to a given surface result.

    :param surface_result: Result of a WCC calculation on a Surface.
    :type surface_result: :class:`.SurfaceResult` or :class:`.SurfaceData`
    
    Example code:
    
    .. code :: python
        
        result = z2pack.surface.run(...)
        print(z2pack.invariant.chern(result)) # Prints the Chern number
    """
    return sum(_pol_step(surface_result.pol))

@export
def z2(surface_result):
    r"""
    Computes the :math:`\mathbb{Z}_2` invariant corresponding to a given surface result.

    :param surface_result: Result of a WCC calculation on a Surface.
    :type surface_result: :class:`.SurfaceResult` or :class:`.SurfaceData`
    
    Example code:
    
    .. code :: python
        
        result = z2pack.surface.run(...)
        print(z2pack.invariant.z2(result)) # Prints the Z2 invariant
    """
    wcc = surface_result.wcc
    gap = surface_result.gap_pos
    inv = 1
    for g1, g2, w2 in zip(gap, gap[1:], wcc[1:]):
        for w in w2:
            inv *= _sgng(g1, g2, w)
    return 1 if inv == -1 else 0
