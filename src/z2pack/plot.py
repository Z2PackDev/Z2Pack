#!/usr/bin/env python
"""This submodule contains all functions for plotting Z2Pack results."""

import colorsys
from types import MappingProxyType

import decorator
import numpy as np

from ._utils import _pol_step

__all__ = [
    "wcc_symmetry",
    "wcc",
    "chern",
    "wcc_3d",
]


def _plot(proj_3d=False):
    """Decorator that sets up the figure axes and handles options common to all plots."""

    @decorator.decorator
    def inner(func, data, *, axis=None, **kwargs):  # pylint: disable=inconsistent-return-statements
        # import is here s.t. the import of the package does not fail
        # if matplotlib is not present
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
        from mpl_toolkits.mplot3d import (  # pylint: disable=import-outside-toplevel,unused-import
            Axes3D,
        )

        # create axis if it does not exist
        if axis is None:
            return_fig = True
            fig = plt.figure()
            axis = fig.add_subplot(111, projection="3d" if proj_3d else None)
        else:
            return_fig = False

        axis.set_xlim(0, 1)
        axis.set_ylim(0, 1)
        if proj_3d:
            axis.set_zlim(0, 1)

        func(data, axis=axis, **kwargs)

        if return_fig:
            return fig

    return inner


def _plot_gaps(surface_result, *, axis, gaps, gap_settings):
    if gaps:
        for offset in [-1, 0, 1]:
            axis.plot(
                surface_result.t,
                [gap_pos % 1 + offset for gap_pos in surface_result.gap_pos],
                **gap_settings,
            )


@_plot()
def wcc_symmetry(
    surface_result,
    *,
    axis=None,
    symmetry_operator,
    wcc_settings=MappingProxyType({"s": 50.0, "lw": 1.0}),
    gaps=True,
    gap_settings=MappingProxyType({"marker": "D", "color": "b", "linestyle": "none"}),
    color_fct=lambda x: colorsys.hsv_to_rgb(
        np.imag(np.log(x)) / (2 * np.pi) % 1,
        min(1, np.exp(-abs(x) + 1)),
        min(1, abs(x)),
    ),
):
    r"""
    Plots the WCCs and the largest gaps (y-axis) against the t-points
    (x-axis). The WCC are colored according to their symmetry expectation value for a given symmetry operator.

    .. note :: This works only if all lines are created from eigenstates, i.e. they are :class:`.EigenstateLineData` instances (not :class:`.WccLineData`).

    :param surface_result:  Result for which the plot is drawn.
    :type surface_result: :class:`.SurfaceResult` or :class:`.SurfaceData`

    :param axis:      Axis where the plot is drawn
    :type axis:       matplotlib.axes.Axes

    :param symmetry_operator:   Symmetry operator according to which the WCC are colored, given as a 2D array.
    :type symmetry_operator:    numpy.array

    :param wcc_settings:    Keyword arguments for the scatter plot of the wcc positions.
    :type wcc_settings:     dict

    :param gaps:    Controls whether the largest gaps are printed.
    :type gaps:     bool

    :param gap_settings:    Keyword arguments for the plot of the gap positions.
    :type gap_settings:     dict

    :param color_fct:   Function converting the symmetry operator eigenvalues to color codes.

    :returns:       :py:class:`matplotlib.figure.Figure` instance (only for ``axis=None``).
    """
    _plot_gaps(surface_result, axis=axis, gaps=gaps, gap_settings=gap_settings)

    for line in surface_result.lines:
        basis_transformation = np.array(line.eigenstates)[0]

        colors = []
        for w_eigenstate in line.wilson_eigenstates:
            colors.append(
                color_fct(
                    np.dot(
                        np.dot(w_eigenstate, basis_transformation),
                        np.dot(
                            symmetry_operator,
                            np.dot(basis_transformation.T, w_eigenstate.T),
                        ),
                    )
                )
            )
        for offset in [-1, 0, 1]:

            axis.scatter(
                [line.t] * len(line.wcc),
                [x % 1 + offset for x in line.wcc],
                facecolors=colors,
                **wcc_settings,
            )


@_plot()
def wcc(
    surface_result,
    *,
    axis=None,
    wcc_settings=MappingProxyType({"s": 50.0, "lw": 1.0, "facecolor": "none", "edgecolors": "k"}),
    gaps=True,
    gap_settings=MappingProxyType({"marker": "D", "color": "b", "linestyle": "none"}),
):
    r"""
    Plots the WCCs and the largest gaps (y-axis) against the t-points (x-axis).

    :param surface_result:  Result for which the plot is drawn.
    :type surface_result: :class:`.SurfaceResult` or :class:`.SurfaceData`

    :param axis:      Axis where the plot is drawn
    :type axis:       matplotlib.axes.Axes

    :param wcc_settings:    Keyword arguments for the scatter plot of the wcc positions.
    :type wcc_settings:     dict

    :param gaps:    Controls whether the largest gaps are shown. Default: ``True``
    :type gaps:     bool

    :param gap_settings:    Keyword arguments for the plot of the gap positions.
    :type gap_settings:     dict

    :returns:       :py:class:`matplotlib.figure.Figure` instance (only for ``axis=None``).
    """
    _plot_gaps(surface_result, axis=axis, gaps=gaps, gap_settings=gap_settings)

    for line in surface_result.lines:
        for offset in [-1, 0, 1]:
            axis.scatter(
                [line.t] * len(line.wcc), [x % 1 + offset for x in line.wcc], **wcc_settings
            )


@_plot()
def chern(
    surface_result,
    *,
    axis=None,
    settings=MappingProxyType({"marker": "o", "markerfacecolor": "r", "color": "r"}),
):
    r"""
    Plots the sum of WCCs (polarization) (y-axis) against the t-points (x-axis).

    :param surface_result:  Result for which the plot is drawn.
    :type surface_result: :class:`.SurfaceResult` or :class:`.SurfaceData`

    :param axis:      Axis where the plot is drawn
    :type axis:       matplotlib.axes.Axes

    :param settings:    Keyword arguments for the plotting function.
    :type settings:     dict

    :returns:       :py:class:`matplotlib.figure.Figure` instance (only for ``axis=None``).
    """
    t_list = surface_result.t
    pol = surface_result.pol
    pol_step = _pol_step(pol)
    for offset in [-1, 0, 1]:
        for t, p_value, p_step in zip(zip(t_list, t_list[1:]), pol, pol_step):
            axis.plot(t, [p_value + offset, p_value + p_step + offset], **settings)
        for t, p_value, p_step in zip(zip(t_list, t_list[1:]), pol[1:], pol_step):
            axis.plot(t, [p_value - p_step + offset, p_value + offset], **settings)


@_plot(proj_3d=True)
def wcc_3d(volume_result, *, axis=None, settings=MappingProxyType({})):
    """
    Plots the WCCs (z-axis) for a volume calculation against their reciprocal space coordinates.

    :param volume_result:  Result for which the plot is drawn.
    :type volume_result: :class:`.VolumeResult` or :class:`.VolumeData`

    :param axis:      Axis where the plot is drawn
    :type axis:       matplotlib.axes.Axes3DSubplot

    :param settings: Settings passed to the ``scatter`` function.
    :type settings: dict
    """
    surface_positions = volume_result.s
    line_positions = volume_result.t
    volume_wcc = volume_result.wcc

    x_values = []
    y_values = []
    z_values = []
    for x, line_pos, surface_wcc in zip(surface_positions, line_positions, volume_wcc):
        for y, line_wcc in zip(line_pos, surface_wcc):
            for z in line_wcc:
                x_values.append(x)
                y_values.append(y)
                z_values.append(z)
    axis.scatter(xs=x_values, ys=y_values, zs=z_values, **settings)
