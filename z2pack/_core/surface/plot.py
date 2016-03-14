#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.02.2016 23:00:28 MST
# File:    _plot.py

import numpy as np
import colorsys

import decorator

from .._utils import _pol_step
from .._result import Result

__all__ = ['wcc_plot', 'wcc_plot_symmetry', 'chern_plot']

@decorator.decorator
def _plot(func, data, *, axis=None, **kwargs):
    # import is here s.t. the import of the package does not fail
    # if matplotlib is not present
    import matplotlib
    import matplotlib.pyplot as plt

    # create axis if it does not exist
    if axis is None:
        return_fig = True
        fig = plt.figure()
        axis = fig.add_subplot(111)
    else:
        return_fig = False

    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)

    func(data, axis=axis, **kwargs)

    if return_fig:
        return fig

def _plot_gaps(surface_result, *, axis, gaps, gap_settings):
    if gaps:
        for offset in [-1, 0, 1]:
            axis.plot(
                surface_result.t,
                [gap_pos % 1 + offset
                    for gap_pos in surface_result.gap_pos
                ],
                **gap_settings
            )

@_plot
def wcc_symmetry(
    surface_result,
    *,
    axis,
    symmetry_operator,
    wcc_settings={'s': 50., 'lw': 1., 'facecolor': 'none'},
    gaps=True,
    gap_settings={'marker': 'D', 'color': 'b', 'linestyle': 'none'},
    color_fct=lambda x: colorsys.hsv_to_rgb(
        np.imag(np.log(x)) / (2 * np.pi) % 1,
        min(1, np.exp(-abs(x) + 1)),
        min(1, abs(x))
    )
):
    r"""
    TODO: FIX!!!

    Plots the WCCs and the largest gaps (y-axis) against the t-points
    (x-axis).
    :param show:    Toggles showing the plot
    :type show:     bool
    :param ax:      Axis where the plot is drawn
    :type ax:       :mod:`matplotlib` ``axis``
    :param shift:   Shifts the plot in the y-axis
    :type shift:    float
    :param wcc_settings:    Keyword arguments for the scatter plot of the wcc
        positions.
    :type wcc_settings:     dict
    :param gaps:    Controls whether the largest gaps are printed.
        Default: ``True``
    :type gaps:     bool
    :param gap_settings:    Keyword arguments for the plot of the gap
        positions.
    :type gap_settings:     dict
    :returns:       :class:`matplotlib figure` instance (only if
        ``ax == None``)
    """
    _plot_gaps(surface_result, axis=axis, gaps=gaps, gap_settings=gap_settings)

    for line in surface_result.lines:
        S = np.array(line.eigenstates)[0]
        wcc = line.wcc

        colors = []
        for v in line.wilson_eigenstates:
            colors.append(color_fct(v @ S @ symmetry_operator @ S.T @ v.T))
        for offset in [-1, 0, 1]:

            axis.scatter([line.t] * len(wcc),
                         [x % 1 + offset for x in wcc],
                         facecolors=colors,
                         **wcc_settings)

@_plot
def wcc(
    surface_result,
    *,
    axis,
    shift=0,
    wcc_settings={'s': 50., 'lw': 1., 'facecolor': 'none'},
    gaps=True,
    gap_settings={'marker': 'D', 'color': 'b', 'linestyle': 'none'}
):
    r"""
    TODO: FIX!!!

    Plots the WCCs and the largest gaps (y-axis) against the t-points
    (x-axis).
    :param show:    Toggles showing the plot
    :type show:     bool
    :param ax:      Axis where the plot is drawn
    :type ax:       :mod:`matplotlib` ``axis``
    :param shift:   Shifts the plot in the y-axis
    :type shift:    float
    :param wcc_settings:    Keyword arguments for the scatter plot of the wcc
        positions.
    :type wcc_settings:     dict
    :param gaps:    Controls whether the largest gaps are printed.
        Default: ``True``
    :type gaps:     bool
    :param gap_settings:    Keyword arguments for the plot of the gap
        positions.
    :type gap_settings:     dict
    :returns:       :class:`matplotlib figure` instance (only if
        ``ax == None``)
    """
    _plot_gaps(surface_result, axis=axis, gaps=gaps, gap_settings=gap_settings)

    for line in surface_result.lines:
        for offset in [-1, 0, 1]:
            wcc = line.wcc
            axis.scatter([line.t] * len(wcc),
                         [(x + shift) % 1 + offset for x in wcc],
                         **wcc_settings)

@_plot
def chern(
    surface_result,
    *,
    axis,
    settings={'marker': 'o', 'markerfacecolor': 'r', 'color': 'r'}
):
    r"""
    TODO
    """
    t_list = surface_result.t
    pol = surface_result.pol
    pol_step = _pol_step(pol)
    for offset in [-1, 0, 1]:
        for i in range(len(pol) - 1):
            axis.plot(t_list[i:i+2], [pol[i] + offset, pol[i] + pol_step[i] + offset], **settings)
        for i in range(len(pol) - 1):
            axis.plot(t_list[i:i+2], [pol[i + 1] - pol_step[i] + offset, pol[i + 1] + offset], **settings)
