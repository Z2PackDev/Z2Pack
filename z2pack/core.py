#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    27.01.2015 11:32:02 CET
# File:    core.py

"""
Implementation of Core functionality
"""

from __future__ import division


from .ptools import string_tools
from .ptools import logger

from . import verbose_prt

import re
import sys
import copy
import pickle
import decorator
import itertools
import numpy as np
import scipy.linalg as la

#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                           LIBRARY CORE                                #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
class System(object):
    r"""
    Describes the interface a Z2Pack specialisation must fulfil. Also, it
    defines the :meth:`surface` method, which is used to create :class:`Surface`
    instances.

    :param m_handle_creator: Takes the ``edge_fct`` and  ``string_vec`` given to :meth:`surface` and creates an ``m_handle`` s.t. ``m_handle(t, N)`` returns the overlap matrices
    :type m_handle_creator: function

    :param kwargs: Keyword arguments are passed to the :class:`Surface` constructor unless overwritten by kwargs to :func:`surface`
    """

    def __init__(self, m_handle_creator, **kwargs):
        self._defaults = kwargs
        self._m_handle_creator = m_handle_creator

    def surface(self, edge_fct, string_vec, **kwargs):
        r"""
        Creates a :class:`Surface` instance.  The surface's position is
        specified by a function ``edge_fct``: :math:`t \in [0, 1]
        \rightarrow \mathbb{R}^3` (or, if you want to stay in the same
        UC, :math:`[0, 1]^3`) connecting a pumping parameter :math:`t`
        to the edge of the surface. The direction along which the surface
        extends from this edge, then, is given by ``string_vec``.

        :param edge_fct: Returns the start of the k-point string
            as function of the pumping parameter t.

        :param string_vec: Direction of the individual k-point strings.
            Note that ``string_vec`` must connect equivalent k-points
            (i.e. it must be a reciprocal lattice vector). Typically,
            it is one of ``[1, 0, 0]``, ``[0, 1, 0]``, ``[0, 0, 1]``.
        :type string_vec: list (float)

        :param kwargs: Keyword arguments are passed to the :class:`Surface`
            constructor. They take precedence over kwargs from the
            :class:`System` constructor.

        :rtype: :class:`Surface`

        .. note:: All directions / positions are given w.r.t. the
            inverse lattice vectors.
        """
        # updating keyword arguments
        kw_arguments = copy.copy(self._defaults)
        kw_arguments.update(kwargs)

        return Surface(self._m_handle_creator(edge_fct, string_vec), edge_fct=edge_fct, **kw_arguments)



class Surface(object):
    r"""
    Describes a surface (or generalised 2D surface) in reciprocal space
    for which the Z2 topological invariant is to be calculated. It is
    created by using the :class:`System`'s :meth:`surface()<System.surface>` method.

    A :class:`Surface` instance is the main object used to perform Z2Pack
    tasks like calculating WCC and the Z2 invariant, getting results, plotting
    etc.

    :param m_handle:        Function that returns a list of overlap matrices
        given the pumping parameter :math:`t` and the number of k-points in
        the string.
    :type m_handle:         function

    :param edge_fct: Returns the start of the k-point string
        as function of the pumping parameter t.

    :param kwargs: Keyword arguments are passed to the :class:`Surface`
        constructor. They take precedence over kwargs from the
        :class:`System` constructor.
    """

    def _validate_kwargs(func=None, target=None):
        """
        checks if kwargs are in target's docstring
        if no target is given, target = func
        """
        @decorator.decorator
        def inner(func, *args, **kwargs):
            """decorated function"""
            if target is None:
                doc = func.__doc__
            else:
                doc = target.__doc__
            valid_kwargs = re.findall(':[\s]*param[\s]+([^:\s]+)', doc)
            for key in kwargs.keys():
                if key not in valid_kwargs:
                    if target is None:
                        raise TypeError(func.__name__ +
                                        ' got an unexpected keyword ' +
                                        key)
                    else:
                        raise TypeError(func.__name__ +
                                        ' got an unexpected keyword \'' +
                                        key + '\' for use in ' +
                                        target.__name__)
            return func(*args, **kwargs)

        if func is None:
            return inner
        else:
            return inner(func)

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

        :param pos_check:           Toggles the automated iteration of the
            number of k-points in a string for convergence of the WCC
            positions. ``Default: True``
        :type pos_check:            bool

        :param gap_check:           Turns on the check for the distance
            between the largest gap and WCC in neighbouring strings.
            ``Default: True``
        :type gap_check:   bool

        :param move_check:       Toggles checking the movement of
            WCC between neighbouring strings. ``Default: True``
        :type move_check:        bool

        :param pos_tol:             Maximum movement of a WCC between two
            steps for convergence. ``Default: 1e-2``
        :type pos_tol:              float

        :param gap_tol:             Smallest tolerated distance between the
            gap and neighbouring WCCs ``Default: 2e-2``
        :type gap_tol:              float

        :param move_tol:   Scaling factor for the maximum allowed
            movement between neighbouring wcc. The factor is multiplied by
            the size of the largest gap between two wcc (from the two
            neighbouring strings, the smaller value is chosen). ``Default: 0.3``
        :type move_tol:    float

        :param iterator:            Generator for the number of points in
            a k-point string. The iterator should also take care of the maximum
            number of iterations. It is needed even when ``pos_check=False``, to
            provide a starting value. ``Default: range(8, 27, 2)``.

        :param min_neighbour_dist:  Minimum distance between two strings (no
            new strings will be added, even if the gap check (gap check & move check) fails).
            ``Default: 0.01``
        :type min_neighbour_dist:   float

        :param use_pickle:          Toggles using the :mod:`pickle` module
            for saving ``Default: True``
        :type use_pickle:           bool

        :param pickle_file:     Path to a file where the results are stored using
            the :py:mod:`pickle` module.
        :type pickle_file:      str

        :param verbose:             Toggles printed output ``Default: True``
        :type verbose:              bool

        :returns:                   ``None``. Use :meth:`get_res` and
            :meth:`invariant` to get the results.
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
                 edge_fct,
                 **kwargs):
        self._m_handle = m_handle
        self._edge_fct = edge_fct
        self._defaults = {'pos_check': True,
                          'gap_check': True,
                          'move_check': True,
                          'pos_tol': 1e-2,
                          'gap_tol': 2e-2,
                          'move_tol': 0.3,
                          'iterator': range(8, 27, 2),
                          'min_neighbour_dist': 0.01,
                          'use_pickle': True,
                          'pickle_file': 'res_pickle.txt',
                          'num_strings': 11,
                          'verbose': True}
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

    @verbose_prt.dispatcher
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

        if not self._current['pos_check']:
            if not(hasattr(self._current['iterator'], '__next__')):
                self._current['iterator'] = iter(self._current['iterator'])
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_check=False
            self._current['iterator'] = [next(self._current['iterator'])]
            del self._current['pos_tol']
        if not self._current['gap_check']:
            del self._current['gap_tol']
        if not self._current['move_check']:
            del self._current['move_tol']
            if self._current['gap_check']:
                del self._current['min_neighbour_dist']

    def _var_init(self):
        """
        initialization - creating data containers
        """
        self._t_points = list(np.linspace(0., 1., self._current['num_strings'],
                                          endpoint=True))
        self._kpt_list = [self._edge_fct(t) for t in self._t_points]
        self._gaps = [None for i in range(self._current['num_strings'])]
        self._gapsize = [None for i in range(self._current['num_strings'])]
        self._wcc_list = [[] for i in range(self._current['num_strings'])]
        self._lambda_list = [[] for i in range(self._current['num_strings'])]
        self._neighbour_check = [False for i in
                                 range(self._current['num_strings'] - 1)]
        self._string_status = [False for i in
                               range(self._current['num_strings'])]

    @verbose_prt.dispatcher
    def _check_neighbours(self):
        """
        checks the neighbour conditions, adds a value in k_points when
        they are not fulfilled
        - adds at most one k_point per run
        - returns Boolean: all neighbour conditions fulfilled <=> True
        """
        if not (self._current['gap_check'] or self._current['move_check']):
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
                                k1 = string_tools.fl_to_s(self._edge_fct(t1), 6)
                                k2 = string_tools.fl_to_s(self._edge_fct(t2), 6)
                                if not neighbour_check:
                                    self._log.log('gap check', t1, k1, t2, k2)
                                if not move_check:
                                    self._log.log('move check', t1, k1, t2, k2)
                            return False
                    else:
                        return False
            return True

    @verbose_prt.dispatcher
    def _check_single_neighbour(self, i):
        """
        Performs the gap check and move check for neighbours at
        i and i + 1
        """
        neighbour_check = True
        move_check = True
        if self._current['gap_check']:
            neighbour_check = self._check_gap_distance(i)
        if self._current['move_check']:
            tolerance = self._current['move_tol'] * min(self._gapsize[i], self._gapsize[i + 1])
            move_check = _convcheck(self._wcc_list[i], self._wcc_list[i + 1], tolerance)
        if neighbour_check and move_check:
            self._neighbour_check[i] = True
        return neighbour_check, move_check

    @verbose_prt.dispatcher
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
            self._kpt_list.insert(i + 1, self._edge_fct(self._t_points[i + 1]))
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
    @verbose_prt.dispatcher
    def _getwcc(self, t):
        """
        calculates WCC along a string by increasing the number of steps
        (k-points) along the string until the WCC converge
        """
        converged = True

        # get new generator
        iterator, self._current['iterator'] = itertools.tee(
            self._current['iterator'], 2)

        N = next(iterator)
        x, min_sv, lambda_ = self._trywcc(self._m_handle(t, N))

        if self._current['pos_check']:
            for N in iterator:
                xold = copy.copy(x)
                x, min_sv, lambda_ = self._trywcc(self._m_handle(t, N))

                # break conditions
                if(_convcheck(x, xold, self._current['pos_tol'])):  # success
                    break
            # iterator ended
            else:
                converged = False
        return sorted(x), lambda_, converged


    @verbose_prt.dispatcher
    def _trywcc(self, all_m):
        """
        Calculates the WCC from the MMN matrices
        """
        lambda_ = np.eye(len(all_m[0]))
        min_sv = 1
        for M in all_m:
            [V, E, W] = la.svd(M)
            lambda_ = np.dot(np.dot(V, W).conjugate().transpose(), lambda_)
            min_sv = min(min(E), min_sv)
        # getting the wcc from the eigenvalues of lambda_
        [eigs, _] = la.eig(lambda_)
        return [(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs], min_sv, lambda_

    #----------------END OF SUPPORT FUNCTIONS---------------------------#

    def log(self):
        """
        Returns the convergence report for the wcc calculation.
        """
        return str(self._log)

    def plot(self,
             shift=0,
             show=True,
             axis=None,
             wcc_settings={'s': 50., 'lw': 1., 'facecolor': 'none'},
             gap_settings={'marker': 'D', 'color': 'b', 'linestyle': 'none'}):
        r"""
        Plots the WCCs and the largest gaps (y-axis) against the t-points 
        (x-axis).

        :param shift:   Shifts the plot in the y-axis
        :type shift:    float

        :param show:    Toggles showing the plot
        :type show:     bool

        :param ax:      Axis where the plot is drawn
        :type ax:       :mod:`matplotlib` ``axis``

        :param wcc_settings:    Keyword arguments for the scatter plot of the wcc
            positions. 

        :param gap_settings:    Keyword arguments for the plot of the gap
            positions. 

        :returns:       :class:`matplotlib figure` instance (only if 
            ``ax == None``)

        .. note:: This plotting tool is meant mainly as a quick way of 
            looking at the results calculated by Z2Pack, and has 
            limited flexibility. If you wish to create beautiful 
            plots, it might be necessary to fetch the data with 
            :meth:`.get_res()` and utilize the full power of matplotlib.
        """
        import matplotlib
        import matplotlib.cbook
        import matplotlib.pyplot as plt
        shift = shift % 1
        if not axis:
            return_fig = True
            fig = plt.figure()
            axis = fig.add_subplot(111)
        else:
            return_fig = False
        axis.set_ylim(0, 1)
        axis.set_xlim(-0.01, 1.01)
        for offset in [-1, 0, 1]:
            axis.plot(self._t_points, [(x + shift) % 1 + offset for x in self._gaps], **gap_settings)
        for i, kpt in enumerate(self._t_points):
            for offset in [-1, 0, 1]:
                axis.scatter([kpt] * len(self._wcc_list[i]),
                             [(x + shift) % 1 + offset for x in self._wcc_list[i]],
                             **wcc_settings)
        if(show):
            plt.show()
        if return_fig:
            return fig

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

    def invariant(self):
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

    # pickle: save and load
    def save(self):
        """
        Saves the t-points, WCC, gap positions and sizes and Lambda \
        matrices to a pickle file.

        Only works if ``use_pickle == True`` and the path to ``pickle_file`` exists.
        """
        to_save = ['_t_points', '_kpt_list', '_wcc_list', '_gaps', '_gapsize', '_lambda_list']
        data = dict((k, v) for k, v in self.__dict__.items() if k in to_save)

        if(self._current['use_pickle']):
            with open(self._current['pickle_file'], "wb") as f:
                pickle.dump(data, f)

    def load(self):
        """
        Loads the data (e.g. from a previous run) from the :mod:`pickle` file.
        """

        with open(self._current['pickle_file'], "rb") as f:
            res = pickle.load(f)

            self.__dict__.update(res)

#-------------------------------------------------------------------#
#                CLASS - independent functions                      #
#-------------------------------------------------------------------#
def _convcheck(list_a, list_b, epsilon):
    """
    new style convergence check!!
    """
    full_list = copy.deepcopy(list_a)
    full_list.extend(list_b)
    gap = _gapfind(full_list)[0]
    a_mod = sorted([(x + 1 - gap) % 1 for x in list_a])
    b_mod = sorted([(x + 1 - gap) % 1 for x in list_b])
    for i in range(len(a_mod)):
        if _dist(a_mod[i], b_mod[i]) > epsilon:
            return False
    else:
        return True
    
def _sgng(z, zplus, x):
    """
    calculates the invariant between two WCC strings
    """
    return -1 if (max(zplus, z) > x and min(zplus, z) < x) else 1

def _gapfind(wcc):
    """
    finds the largest gap in vector wcc, modulo 1
    """
    wcc = sorted(wcc)
    gapsize = 0
    gappos = 0
    N = len(wcc)
    for i in range(0, N - 1):
        temp = wcc[i + 1] - wcc[i]
        if(temp > gapsize):
            gapsize = temp
            gappos = i
    temp = wcc[0] - wcc[-1] + 1
    if(temp > gapsize):
        gapsize = temp
        gappos = N - 1
    return (wcc[gappos] + gapsize / 2) % 1, gapsize

def _dist(x, y):
    """
    Returns the smallest distance on the periodic [0, 1) between x, y
    where x, y should be in [0, 1)
    """
    x = x % 1
    y = y % 1
    return min(abs(1 + x - y) % 1, abs(1 - x + y) % 1)


#----------------END CLASS INDEPENDENT FUNCTIONS---------------------#
