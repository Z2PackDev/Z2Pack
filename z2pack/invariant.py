#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This submodule contains functions for calculating the topological invariants from the result of a WCC / Wilson loop calculation.
"""

from fsc.export import export

from ._utils import _pol_step, _sgng, _check_kramers_pairs

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
def z2(surface_result, check_kramers_pairs=True):
    r"""
    Computes the :math:`\mathbb{Z}_2` invariant corresponding to a given surface result.

    :param surface_result: Result of a WCC calculation on a Surface.
    :type surface_result: :class:`.SurfaceResult` or :class:`.SurfaceData`

    :param check_kramers_pairs: Check whether the WCC at the edge of the surface come in degenerate pairs. This is a requirement for having a well-defined Z2 invariant.
    :type check_kramers_pairs: bool

    Example code:

    .. code :: python

        result = z2pack.surface.run(...)
        print(z2pack.invariant.z2(result)) # Prints the Z2 invariant
    """
    wcc = surface_result.wcc
    if check_kramers_pairs and wcc:
        if not (
            _check_kramers_pairs(list(wcc[0])) and
            _check_kramers_pairs(list(wcc[-1]))
        ):
            raise ValueError('The given WCC are not degenerate Kramers pairs at the edges of the surface.')
    gap = surface_result.gap_pos
    inv = 1
    for g1, g2, w2 in zip(gap, gap[1:], wcc[1:]):
        for w in w2:
            inv *= _sgng(g1, g2, w)
    return 1 if inv == -1 else 0
