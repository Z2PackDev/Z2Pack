#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
def z2(surface_result):  # pylint: disable=invalid-name
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
    for gap_left, gap_right, wcc_right in zip(gap, gap[1:], wcc[1:]):
        for wcc_pos in wcc_right:
            inv *= _sgng(gap_left, gap_right, wcc_pos)
    return 1 if inv == -1 else 0
