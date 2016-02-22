#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.02.2016 23:00:28 MST
# File:    _plot.py

from ...common.decorator_proxy import decorator

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

    # see if data is actually a Result object
    try:
        data = data.data
    except AttributeError:
        pass
        
    func(data, axis=axis, **kwargs)

    if return_fig:
        return fig

@_plot
def wcc_plot(
    surface_data,
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
    if gaps:
        for offset in [-1, 0, 1]:
            axis.plot(
                surface_data.t,
                [(line.result.data.gap_pos + shift) % 1 + offset
                    for line in surface_data.lines
                ],
                **gap_settings
            )
    for line in surface_data.lines:
        for offset in [-1, 0, 1]:
            wcc = line.result.data.wcc
            axis.scatter([line.t] * len(wcc),
                         [(x + shift) % 1 + offset for x in wcc],
                         **wcc_settings)
