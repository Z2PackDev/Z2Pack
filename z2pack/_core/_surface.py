#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 12:00:56 CEST
# File:    _surface.py

from __future__ import division

from ..ptools import logger

from ._verbose_prt import dispatcher_surface as prt_dispatcher
from ._utils import *
from ._kwarg_validator import _validate_kwargs
from ._line import Line

import re
import sys
import copy
import pickle
import warnings
import decorator
import itertools
import numpy as np
import scipy.linalg as la

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

    :param kwargs: Keyword arguments are passed to the :class:`Surface`
        constructor. They take precedence over kwargs from the
        :class:`System` constructor.
    """

    @_validate_kwargs
    def wcc_calc(self, **kwargs):
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
            ``Default: 1e-2``
        :type pos_tol:              float

        :param gap_tol:     Smallest distance between a gap and its
            neighbouring WCC for the gap check to be satisfied.
            The check can be turned off by setting ``gap_tol=None``.
            ``Default: 2e-2``
        :type gap_tol:              float

        :param move_tol:    Scaling factor for the maximum allowed
            movement between neighbouring wcc. The factor is multiplied by
            the size of the largest gap between two wcc (from the two
            neighbouring strings, the smaller value is chosen). The check
            can be turned off by setting ``move_tol=None``.
            ``Default: 0.3``
        :type move_tol:    float

        :param iterator:            Generator for the number of points in
            a k-point string. The iterator should also take care of the maximum
            number of iterations. It is needed even when ``pos_tol=None``, to
            provide a starting value. ``Default: range(8, 27, 2)``.

        :param min_neighbour_dist:  Minimum distance between two strings (no
            new strings will be added, even if the gap check (gap check & move check) fails).
            ``Default: 0.01``
        :type min_neighbour_dist:   float

        :param pickle_file:     Path to a file where the results are stored using
            the :py:mod:`pickle` module. Can be ``None`` to disable pickling.
        :type pickle_file:      str

        :param verbose:             Toggles printed output ``Default: True``
        :type verbose:              bool

        :param overwrite:           Toggles whether existing data should be
            overwritten or used to re-start a run.
        :type overwrite:            bool

        :returns:                   ``None``. Use :meth:`get_res` and
            :meth:`z2` to get the results.
        """
        self._current = copy.deepcopy(self._defaults)
        self._current.update(kwargs)
        self._param_check()
        self._log.reset()
        self._wcc_calc_main()

    # has to be below wcc_calc because _validate_kwargs needs access to
    # wcc_calc.__doc__
    @_validate_kwargs(target=wcc_calc)
    def __init__(self,
                 m_handle,
                 param_fct,
                 **kwargs):
        self._m_handle = m_handle
        self._param_fct = param_fct
        self._defaults = {
                          'pos_tol': 1e-2,
                          'gap_tol': 2e-2,
                          'move_tol': 0.3,
                          'iterator': range(8, 27, 2),
                          'min_neighbour_dist': 0.01,
                          'pickle_file': 'res_pickle.txt',
                          'num_strings': 11,
                          'verbose': True,
                          'overwrite': False,
                          }
        self._defaults.update(kwargs)
        self._current = copy.deepcopy(self._defaults)
        self._log = logger.Logger(logger.ConvFail('pos check', 't = {}, k = {}'),
                                   logger.ConvFail('gap check',
                                    'between t = {}, k = {}\n    and t = {}, k = {}'),
                                   logger.ConvFail('move check',
                                    'between t = {}, k = {}\n    and t = {}, k = {}'))

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
        self._var_init()
        while not (all(self._neighbour_check)):
            for i, t in enumerate(self._t_points):
                if not(self._string_status[i]):
                    self._wcc_list[i], self._lambda_list[i] = self._getwcc(t)
                    self._gaps[i], self._gapsize[i] = _gapfind(self._wcc_list[i])
                    self._string_status[i] = True
                    self.save()

            if self._check_neighbours() is None:
                break

    def _param_check(self):
        """
        Checks the current parameters and deletes unnecessary ones.
        """
        if(self._current['num_strings'] < 2):
            raise ValueError("num_strings must be at least 2")

        if self._current['pos_tol'] is None:
            if not(hasattr(self._current['iterator'], '__next__')):
                self._current['iterator'] = iter(self._current['iterator'])
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self._current['iterator'] = [next(self._current['iterator'])]
        if (self._current['gap_tol'] is None) and (self._current['move_tol'] is None):
            del self._current['min_neighbour_dist']

    def _var_init(self):
        """
        initialization - creating data containers
        """
        if (not hasattr(self, '_wcc_list')) or self._current['overwrite']:
            self._wcc_list = [[] for i in range(self._current['num_strings'])]
            self._t_points = list(np.linspace(0., 1., self._current['num_strings'],
                                              endpoint=True))
            self._kpt_list = [self._param_fct(t, 0.) for t in self._t_points]
            self._gaps = [None for i in range(self._current['num_strings'])]
            self._gapsize = [None for i in range(self._current['num_strings'])]
            self._lambda_list = [[] for i in range(self._current['num_strings'])]
            self._string_status = [False for i in
                                   range(self._current['num_strings'])]
        # this is DELIBERATELY always overwritten to allow changing the
        # move_tol and gap_tol parameters between reloaded runs.
        # It is inexpensive to recreate in the opposite case. 
        self._neighbour_check = [False for i in
                                 range(len(self._wcc_list) - 1)]

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
            move_check = _convcheck(self._wcc_list[i], self._wcc_list[i + 1], tolerance)
        if neighbour_check and move_check:
            self._neighbour_check[i] = True
        return neighbour_check, move_check

    @prt_dispatcher
    def _add_string(self, i):
        """
        Adds a string between i and i + 1. returns False if it failed
        due to the minimum neighbour distance, True else.
        """
        if(self._t_points[i + 1] - self._t_points[i] <
           self._current['min_neighbour_dist']):
            self._neighbour_check[i] = True
            return False
        else:
            self._neighbour_check.insert(i + 1, False)
            self._string_status.insert(i + 1, False)
            self._t_points.insert(i + 1, (self._t_points[i] +
                                  self._t_points[i + 1]) / 2)
            self._kpt_list.insert(i + 1, self._param_fct(self._t_points[i + 1], 0.))
            self._wcc_list.insert(i + 1, [])
            self._lambda_list.insert(i + 1, [])
            self._gaps.insert(i + 1, None)
            self._gapsize.insert(i + 1, None)
        return True

    def _check_gap_distance(self, i):
        """
        checks if gap is too close to any of the elements in wcc
        """
        for wcc_val in self._wcc_list[i + 1]:
            if _dist(wcc_val, self._gaps[i]) < self._current['gap_tol']:
                return False
        return True

    # calculating one string
    @prt_dispatcher
    def _getwcc(self, t):
        """
        calculates WCC along a string by increasing the number of steps
        (k-points) along the string until the WCC converge
        """
        param_fct_line = lambda kx: self._param_fct(t, kx)
        line = Line(self._m_handle, param_fct_line, pos_tol=self._current['pos_tol'], iterator=self._current['iterator'], verbose=self._current['verbose'])
        line.wcc_calc()
        res = line.get_res()
        return res['wcc'], res['lambda'], res['converged']
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
        if(show):
            plt.show()
        if return_fig:
            return fig

    @_plot
    def wcc_plot(self,
             show=True,
             axis=None,
             shift=0,
             wcc_settings={'s': 50., 'lw': 1., 'facecolor': 'none'},
             gaps=True,
             gap_settings={'marker': 'D', 'color': 'b', 'linestyle': 'none'}):
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
                axis.scatter([kpt] * len(self._wcc_list[i]),
                             [(x + shift) % 1 + offset for x in self._wcc_list[i]],
                             **wcc_settings)

    def plot(self, *args, **kwargs):
        r"""
        Deprecated alias for :meth:`wcc_plot`.
        """
        warnings.warn('Using deprecated function plot. Use wcc_plot instead.',
            DeprecationWarning, stacklevel=2)
        return self.wcc_plot(*args, **kwargs)

    @_plot
    def chern_plot(self,
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
        ``lambda_``, a list of Gamma matrices for each string.
        """
        return {'t_par': self._t_points, 'kpt': self._kpt_list, 'wcc': self._wcc_list, 'gap': self._gaps, 'lambda_': self._lambda_list}

    def z2(self):
        """
        Calculates the Z2 topological invariant.

        :returns:   Z2 topological invariant
        :rtype:     int
        """
        try:
            inv = 1
            for i in range(0, len(self._wcc_list)-1):
                for j in range(0, len(self._wcc_list[0])):
                    inv *= _sgng(self._gaps[i],
                                 self._gaps[i+1],
                                 self._wcc_list[i+1][j])

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
        pol = [sum(wcc) % 1 for wcc in self._wcc_list]
        delta_pol = []
        for i in range(len(pol) - 1):
            diff = pol[i + 1] - pol[i]
            delta_pol.append(min([diff, diff + 1, diff - 1], key=lambda x: abs(x)))
        return {'chern': sum(delta_pol), 'pol': pol, 'step': delta_pol}

    # pickle: save and load
    def save(self):
        """
        Saves the data (t-points, k-points, wcc, gaps, gap sizes,
        lambda matrices, string statuses) to a pickle file.

        Only works if ``pickle_file`` is not ``None`` and the path to ``pickle_file`` exists.
        """
        to_save = ['_t_points', '_kpt_list', '_wcc_list', '_gaps', '_gapsize', '_lambda_list', '_string_status']
        data = dict((k, v) for k, v in self.__dict__.items() if k in to_save)

        if self._current['pickle_file'] is not None:
            with open(self._current['pickle_file'], "wb") as f:
                pickle.dump(data, f)

    def load(self, quiet=False):
        r"""
        Loads the data (e.g. from a previous run) from the :mod:`pickle` file.

        :param quiet:   If True, load does not raise an Error if there is
            no pickle file. Default: ``False``
        :type quiet:    bool
        """
        try:
            with open(self._current['pickle_file'], "rb") as f:
                res = pickle.load(f)
                self.__dict__.update(res)
        except IOError as e:
            if not quiet:
                raise e
