#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 12:00:56 CEST
# File:    _surface.py

from __future__ import division

from ..ptools import logger, string_tools

from ._surface_prt import prt_dispatcher
from ._utils import *
from ._line import Line

import pickle
import warnings
import decorator
import functools
import numpy as np

class Surface(object):
    r"""
    Describes a surface (or generalised 2D surface) in reciprocal space
    for which topological invariants are to be calculated. It is
    created by using the :class:`System`'s :meth:`surface()<System.surface>` method.

    A :class:`Surface` instance is the main object used to perform Z2Pack
    tasks like calculating WCC, Chern number and the Z2 invariant, getting
    results, plotting etc.

    :param m_handle:        Function that returns a list of overlap matrices
        given the pumping parameter :math:`t` and the number of k-points in
        the string.
    :type m_handle:         function

    :param param_fct: Returns the start of the k-point string
        as function of the pumping parameter t.

    :param pickle_file:     Path to a file where the results are stored using
        the :py:mod:`pickle` module. Can be ``None`` to disable pickling.
    :type pickle_file:      str
    """
    def __init__(self, m_handle, param_fct, pickle_file=None):
        self._m_handle = m_handle
        self._param_fct = param_fct
        self._pickle_file = pickle_file
        self._log = logger.Logger(
            logger.ConvFail('pos check', 't = {0}, k = {1}'),
            logger.ConvFail('gap check',
                            'between t = {0}, k = {1}\n    and t = {2}, k = {3}'),
            logger.ConvFail('move check',
                            'between t = {0}, k = {1}\n    and t = {2}, k = {3}'))
        self._var_init()

    def wcc_calc(
        self,
        pos_tol=1e-2,
        gap_tol=2e-2,
        move_tol=0.3,
        iterator=range(8, 27, 2),
        min_neighbour_dist=0.01,
        num_strings=11,
        verbose=True,
        overwrite=False
    ):
        r"""
        Calculates the Wannier charge centers in the given surface

        * automated convergence in string direction
        * automated check for distance between gap and wcc -> add string
        * automated convergence check w.r.t. movement of the WCC between
          different k-strings.

        :param num_strings:         Initial number of strings ``Default: 11``
        :type num_strings:          int

        :param pos_tol:     The maximum movement of a WCC for the iteration
            w.r.t. the number of k-points in a single string to converge.
            The iteration can be turned off by setting ``pos_tol=None``.
        :type pos_tol:              float

        :param gap_tol:     Smallest distance between a gap and its
            neighbouring WCC for the gap check to be satisfied.
            The check can be turned off by setting ``gap_tol=None``.
        :type gap_tol:              float

        :param move_tol:    Scaling factor for the maximum allowed
            movement between neighbouring wcc. The factor is multiplied by
            the size of the largest gap between two wcc (from the two
            neighbouring strings, the smaller value is chosen). The check
            can be turned off by setting ``move_tol=None``.
        :type move_tol:    float

        :param iterator:            Generator for the number of points in
            a k-point string. The iterator should also take care of the maximum
            number of iterations. It is needed even when ``pos_tol=None``, to
            provide a starting value.

        :param min_neighbour_dist:  Minimum distance between two strings (no
            new strings will be added, even if the gap check (gap check & move check) fails).
        :type min_neighbour_dist:   float

        :param verbose:             Toggles printed output.
        :type verbose:              bool

        :param overwrite:           Toggles whether existing data should be
            overwritten or used to re-start a run.
        :type overwrite:            bool

        :returns:                   ``None``. Use :meth:`get_res` and
            :meth:`z2` to get the results.
        """
        self._current = {key: value for key, value in locals().items() if key != 'self'}
        self._param_check()
        self._log.reset()
        self._wcc_calc_main()


    #-------------------------------------------------------------------#
    #                support functions for wcc                          #
    #-------------------------------------------------------------------#

    @prt_dispatcher
    def _wcc_calc_main(self):
        """
        main calculation part
        all gap checks can be true even if it did not converge!
        a failed convergence (reaching lower limit) also produces
        'true'
        """
        self._var_refresh()
        while not all(self._neighbour_check):
            for i, t in enumerate(self._t_points):
                if not self._string_status[i]:
                    self._call_line(i, t)
                    self._gaps[i], self._gapsize[i] = _gapfind(self._line_list[i].wcc)
                    self._string_status[i] = True
                    self.save()

            if self._check_neighbours() is None:
                break

    def _param_check(self):
        """
        Checks the current parameters and deletes unnecessary ones.
        """
        if self._current['num_strings'] < 2:
            raise ValueError("num_strings must be at least 2")

        if self._current['pos_tol'] is None:
            if not hasattr(self._current['iterator'], '__next__'):
                self._current['iterator'] = iter(self._current['iterator'])
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self._current['iterator'] = [next(self._current['iterator'])]

    def _var_init(self):
        """
        initialization - creating data containers
        """
        self._line_list = []
        self._t_points = []
        self._kpt_list = []
        self._gaps = []
        self._gapsize = []
        self._neighbour_check = []
        self._string_status = []

    @prt_dispatcher
    def _var_refresh(self):
        """
        refresh variables for wcc_calc
        """
        if self._current['overwrite']:
            self._var_init()
        # this is DELIBERATELY always overwritten to allow changing the
        # move_tol, gap_tol, pos_tol, num_strings parameters between reloaded runs.
        # It is inexpensive to recreate in the opposite case.
        for t in np.linspace(0., 1., self._current['num_strings'], endpoint=True):
            self._add_string_at(t)
        self._neighbour_check = [False for i in
                                 range(len(self._line_list) - 1)]
        self._string_status = [False for i in
                               range(len(self._line_list))]

    @prt_dispatcher
    def _check_neighbours(self):
        """
        checks the neighbour conditions, adds a value in k_points when
        they are not fulfilled
        - adds at most one k_point per run
        - returns Boolean: all neighbour conditions fulfilled <=> True
        """
        if (self._current['gap_tol'] is None) and (self._current['move_tol'] is None):
            return None
        else:
            for i, status in enumerate(self._neighbour_check):
                if not status:
                    if self._string_status[i] and self._string_status[i + 1]:
                        neighbour_check, move_check = self._check_single_neighbour(i)
                        if not (neighbour_check and move_check):
                            if not self._add_string(i):
                                t1 = self._t_points[i]
                                t2 = self._t_points[i + 1]
                                k1 = string_tools.fl_to_s(self._param_fct(t1, 0.), 6)
                                k2 = string_tools.fl_to_s(self._param_fct(t2, 0.), 6)
                                if not neighbour_check:
                                    self._log.log('gap check', t1, k1, t2, k2)
                                if not move_check:
                                    self._log.log('move check', t1, k1, t2, k2)
                            return False
                    else:
                        return False
            return True

    @prt_dispatcher
    def _check_single_neighbour(self, i):
        """
        Performs the gap check and move check for neighbours at
        i and i + 1
        """
        neighbour_check = True
        move_check = True
        if self._current['gap_tol'] is not None:
            neighbour_check = self._check_gap_distance(i)
        if self._current['move_tol'] is not None:
            tolerance = self._current['move_tol'] * min(self._gapsize[i], self._gapsize[i + 1])
            move_check, _ = _convcheck(self._line_list[i].wcc, self._line_list[i + 1].wcc, tolerance)
        if neighbour_check and move_check:
            self._neighbour_check[i] = True
        return neighbour_check, move_check

    @prt_dispatcher
    def _add_string_at(self, t):
        r"""
        Adds a string at a specific pumping parameter t. Returns False if it failed due to the minimum neighbour distance, True else.
        """
        for i, tval in enumerate(self._t_points):
            if tval > t:
                pos = i
                break
        else:
            pos = len(self._t_points)
        # check if string already exists (up to min_neighbour_dist tolerance)
        try:
            if abs(self._t_points[pos - 1] - t) < self._current['min_neighbour_dist']:
                return False
        except IndexError:
            pass
        try:
            if abs(self._t_points[pos] - t) < self._current['min_neighbour_dist']:
                return False
        except IndexError:
            pass
        self._neighbour_check.insert(pos, False)
        self._string_status.insert(pos, False)
        self._t_points.insert(pos, t)
        self._kpt_list.insert(pos, self._param_fct(self._t_points[pos], 0.))
        self._line_list.insert(pos, None)
        self._gaps.insert(pos, None)
        self._gapsize.insert(pos, None)
        return True

    @prt_dispatcher
    def _add_string(self, i):
        """
        Adds a string between i and i + 1. Returns False if it failed
        due to the minimum neighbour distance, True else.
        """
        if(self._t_points[i + 1] - self._t_points[i] <
           self._current['min_neighbour_dist']):
            self._neighbour_check[i] = True
            return False
        else:
            self._neighbour_check.insert(i + 1, False)
            self._string_status.insert(i + 1, False)
            self._t_points.insert(i + 1, (self._t_points[i] + self._t_points[i + 1]) / 2)
            self._kpt_list.insert(i + 1, self._param_fct(self._t_points[i + 1], 0.))
            self._line_list.insert(i + 1, None)
            self._gaps.insert(i + 1, None)
            self._gapsize.insert(i + 1, None)
        return True

    def _check_gap_distance(self, i):
        """
        checks if gap is too close to any of the elements in wcc
        """
        for wcc_val in self._line_list[i + 1].wcc:
            if _dist(wcc_val, self._gaps[i]) < self._current['gap_tol']:
                return False
        return True

    # calculating one string
    @prt_dispatcher
    def _call_line(self, i, t):
        r"""
        Creates the Line object if necessary and makes the call to its wcc_calc
        """
        if self._line_list[i] is None:
            param_fct_line = lambda kx: self._param_fct(t, kx)
            self._line_list[i] = Line(self._m_handle, param_fct_line)
        self._line_list[i].wcc_calc(pos_tol=self._current['pos_tol'], iterator=self._current['iterator'], verbose='reduced' if self._current['verbose'] else False)
        # get convergence flag to print function
        return self._line_list[i].get_res()['converged']
    #----------------END OF SUPPORT FUNCTIONS---------------------------#

    def log(self):
        """
        Returns the convergence report for the wcc calculation.
        """
        return str(self._log)

    @decorator.decorator
    def _plot(func, self, show, axis, *args, **kwargs):
        import matplotlib
        import matplotlib.cbook
        import matplotlib.pyplot as plt
        if axis is None:
            return_fig = True
            fig = plt.figure()
            axis = fig.add_subplot(111)
        else:
            return_fig = False
        axis.set_ylim(0, 1)
        axis.set_xlim(-0.01, 1.01)
        axis.set_xticks(self._t_points, minor=True)
        func(self, show, axis, *args, **kwargs)
        if show:
            plt.show()
        if return_fig:
            return fig

    @_plot
    def wcc_plot(
        self,
        show=True,
        axis=None,
        shift=0,
        wcc_settings={'s': 50., 'lw': 1., 'facecolor': 'none'},
        gaps=True,
        gap_settings={'marker': 'D', 'color': 'b', 'linestyle': 'none'}
    ):
        r"""
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
                axis.plot(self._t_points, [(x + shift) % 1 + offset for x in self._gaps], **gap_settings)
        for i, kpt in enumerate(self._t_points):
            for offset in [-1, 0, 1]:
                axis.scatter([kpt] * len(self._line_list[i].wcc),
                             [(x + shift) % 1 + offset for x in self._line_list[i].wcc],
                             **wcc_settings)

    def plot(self, *args, **kwargs):
        r"""
        Deprecated alias for :meth:`wcc_plot`.
        """
        warnings.warn('Using deprecated function plot. Use wcc_plot instead.',
                      DeprecationWarning, stacklevel=2)
        return self.wcc_plot(*args, **kwargs)

    @_plot
    def chern_plot(
        self,
        show=True,
        axis=None,
        settings={'marker': 'o', 'markerfacecolor': 'r', 'color': 'r'},
    ):
        r"""
        Plots the evolution of the polarization (sum of WCC) along the
        surface against the t-points.

        :param show:    Toggles showing the plot
        :type show:     bool

        :param ax:      Axis where the plot is drawn
        :type ax:       :mod:`matplotlib` ``axis``

        :param settings:    Keyword arguments passed to ``matplotlib.pyplot.plot()``
        :type settings:     dict
        """
        res = self.chern()
        pol = res['pol']
        steps = res['step']
        for offset in [-1, 0, 1]:
            for i in range(len(pol) - 1):
                axis.plot(self._t_points[i:i+2], [pol[i] + offset, pol[i] + steps[i] + offset], **settings)
            for i in range(len(pol) - 1):
                axis.plot(self._t_points[i:i+2], [pol[i + 1] - steps[i] + offset, pol[i + 1] + offset], **settings)

    def get_res(self):
        """
        Returns a ``dict`` with the following keys: ``t_par``, the \
        pumping parameters t used (at which the WCCs were \
        computed), ``kpt`` The list of starting points for each k-point\
         string, ``wcc``, the WCC positions at each of those positions, \
        ``gap`` the positions of the largest gap in each string and \
        ``lambda``, a list of Gamma matrices for each string.
        """
        return {'t_par': self._t_points, 'kpt': self._kpt_list, 'wcc': [line.wcc if line is not None else None for line in self._line_list], 'gap': self._gaps, 'lambda_': [line.lambda_ if line is not None else None for line in self._line_list]}

    def z2(self):
        """
        Calculates the Z2 topological invariant.

        :returns:   Z2 topological invariant
        :rtype:     int
        """
        try:
            inv = 1
            for i in range(0, len(self._line_list)-1):
                for j in range(0, len(self._line_list[0].wcc)):
                    inv *= _sgng(self._gaps[i],
                                 self._gaps[i+1],
                                 self._line_list[i+1].wcc[j])

            return 1 if inv == -1 else 0
        except (NameError, AttributeError):
            raise RuntimeError('WCC not yet calculated')

    def invariant(self):
        r"""
        Deprecated alias for :meth:`z2`.
        """
        warnings.warn('Using deprecated function invariant. Use z2 instead.',
                      DeprecationWarning, stacklevel=2)
        return self.z2()

    def chern(self):
        r"""
        Calculates the evolution of polarization (sum of WCC) along the
        pumping cycle, as well as the Chern number. To estimate convergence,
        the largest jump in polarization is also calculated.

        :returns:   A ``dict`` containing Chern number (``chern``), polarization evolution (``pol``), and the steps between the polarization values (``step``).
        """
        pol = [sum(line.wcc) % 1 for line in self._line_list]
        delta_pol = []
        for i in range(len(pol) - 1):
            diff = pol[i + 1] - pol[i]
            delta_pol.append(min([diff, diff + 1, diff - 1], key=abs))
        return {'chern': sum(delta_pol), 'pol': pol, 'step': delta_pol}

    # pickle: save and load
    def save(self):
        """
        Saves the data (t-points, k-points, wcc, gaps, gap sizes,
        lambda matrices, string statuses) to a pickle file.

        Only works if ``pickle_file`` is not ``None`` and the path to ``pickle_file`` exists.
        """

        to_save = ['_t_points', '_kpt_list', '_gaps', '_gapsize', '_line_list']
        data = dict((k, v) for k, v in self.__dict__.items() if k in to_save)

        if self._pickle_file is not None:
            with open(self._pickle_file, "wb") as f:
                pickle.dump(data, f)

    def load(self, quiet=False):
        r"""
        Loads the data (e.g. from a previous run) from the :mod:`pickle` file.

        :param quiet:   If True, load does not raise an Error if there is
            no pickle file. Default: ``False``
        :type quiet:    bool
        """
        try:
            with open(self._pickle_file, "rb") as f:
                res = pickle.load(f)
                self.__dict__.update(res)
            # restore Line objects
            for t, line in zip(self._t_points, self._line_list):
                if line is not None:
                    line.inject(self._m_handle, functools.partial(self._param_fct, t))
        except IOError as e:
            if not quiet:
                raise e
