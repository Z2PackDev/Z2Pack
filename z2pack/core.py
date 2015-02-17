#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    27.01.2015 11:32:02 CET
# File:    core.py

"""
Implementation of Core functionality
"""

from __future__ import division, print_function


from .ptools import string_tools
from .ptools import logger

from . import verbose_prt


import re
import sys
import time
import copy
import pickle
import decorator
import itertools
import numpy as np
import scipy.linalg as la
import matplotlib
import matplotlib.cbook
import matplotlib.pyplot as plt


#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                           LIBRARY CORE                                #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
class System:
    r"""
    Describes the interface a Z2Pack specialisation must fulfil. Also, it
    defines the :meth:`surface` method, which is used to create :class:`Surface`
    instances.

    :param m_handle_creator: Takes the ``edge_function`` and  ``string_vec`` given to :meth:`surface` and creates an ``m_handle`` s.t. ``m_handle(t, N)`` returns the overlap matrices
    :type m_handle_creator: function

    :param kwargs: Keyword arguments are passed to the :class:`Surface` constructor unless overwritten by kwargs to :func:`surface`
    """

    def __init__(self, m_handle_creator, **kwargs):
        self._defaults = kwargs
        self._m_handle_creator = m_handle_creator

    def surface(self, edge_function, string_vec, **kwargs):
        r"""
        Creates a :class:`Surface` instance.  The surface's position is
        specified by a function ``edge_function``: :math:`t \in [0, 1]
        \rightarrow \mathbb{R}^3` (or, if you want to stay in the same
        UC, :math:`[0, 1]^3`) connecting a pumping parameter :math:`t`
        to the edge of the surface. The direction along which the surface
        extends from this edge, then, is given by ``string_vec``.

        :param edge_function: Returns the start of the k-point string 
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

        return Surface(self._m_handle_creator(edge_function, string_vec), edge_function=edge_function, **kw_arguments)



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
    
    :param edge_function: Returns the start of the k-point string 
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
            valid_kwargs = [text.lstrip(' ').split(':')[0]
                            for text in doc.split(':param')[1:]]
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

        :param no_iter:             Turns the automated iteration of the  
            number of k-points in a string off ``Default: False``
        :type no_iter:              bool

        :param no_neighbour_check:  Turns the automated check for missing  
            strings (by distance between gaps and WCCs) off ``Default: False``
        :type no_neighbour_check:   bool

        :param no_move_check:       Toggles checking the movement of 
            neighbouring wcc. ``Default: False``
        :type no_move_check:        bool

        :param wcc_tol:             Maximum movement of a WCC between two  
            steps for convergence. ``Default: 1e-2``
        :type wcc_tol:              float

        :param gap_tol:             Smallest tolerated distance between the 
            gap and neighbouring WCCs ``Default: 2e-2``
        :type gap_tol:              float

        :param move_check_factor:   Scaling factor for the maximum allowed 
            movement between neighbouring wcc. The factor is multiplied by 
            the size of the largest gap between two wcc (from the two 
            neighbouring strings, the smaller value is chosen). ``Default: 0.5``
        :type move_check_factor:    float

        :param iterator:            Generator for the number of points in 
            a k-point string. The iterator should also take care of the maximum 
            number of iterations. It is needed even when ``no_iter=True``, to 
            provide a starting value. ``Default: range(8, 27, 2)``.

        :param min_neighbour_dist:  Minimum distance between two strings (no 
            new strings will be added, even if the neighbour check fails). 
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

        #----------------checking input variables-----------------------#
        self._current = copy.deepcopy(self._defaults)
        self._current.update(kwargs)

        # checking num_strings
        if(self._current['num_strings'] < 2):
            raise ValueError("num_strings must be at least 2")

        if self._current['no_iter']:
            if not(hasattr(self._current['iterator'], '__next__')):
                self._current['iterator'] = iter(self._current['iterator'])
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect no_iter=True
            self._current['iterator'] = [next(self._current['iterator'])]
            del self._current['wcc_tol']
        if self._current['no_neighbour_check']:
            del self._current['gap_tol']
        if self._current['no_move_check']:
            del self._current['move_check_factor']
            if self._current['no_neighbour_check']:
                del self._current['min_neighbour_dist']

        # reset log to avoid double-logging
        self._log.reset()

        #----------------initial output---------------------------------#
        string = "starting wcc calculation\n\n"
        length = max(len(key) for key in self._current.keys()) + 2
        for key in sorted(self._current.keys()):
            value = str(self._current[key])
            if(len(value) > 48):
                value = value[:45] + '...'
            string += key.ljust(length) + value + '\n'
        string = string[:-1]
        self._print(string_tools.cbox(string) + '\n')

        start_time = time.time()

        #----------------initialization - creating data containers------#
        self._t_points = list(np.linspace(0., 1., self._current['num_strings'],
                                          endpoint=True))
        self._kpt_list = [self._edge_function(t) for t in self._t_points]
        self._gaps = [None for i in range(self._current['num_strings'])]
        self._gapsize = [None for i in range(self._current['num_strings'])]
        self._wcc_list = [[] for i in range(self._current['num_strings'])]
        self._lambda_list = [[] for i in range(self._current['num_strings'])]
        self._neighbour_check = [False for i in
                                 range(self._current['num_strings'] - 1)]
        self._string_status = [False for i in
                               range(self._current['num_strings'])]

        # main calculation part
        # all neighbour checks can be true even if it did not converge!
        # a failed convergence (reaching lower limit) also produces
        # 'true'
        while not (all(self._neighbour_check)):
            for i, t in enumerate(self._t_points):
                if not(self._string_status[i]):
                    self._wcc_list[i], self._lambda_list[i] = self._getwcc(t)
                    self._gaps[i], self._gapsize[i] = _gapfind(self._wcc_list[i])
                    self._string_status[i] = True
                    self.save()

            if not(self._current['no_neighbour_check'] and self._current['no_move_check']):
                self._check_neighbours()
            else:
                self._print('skipping neighbour checks')
                break

        # dump results into pickle file
        self.save()

        # output to signal end of wcc calculation
        end_time = time.time()
        duration = end_time - start_time
        duration_string = str(int(np.floor(duration / 3600))) + \
            " h " + str(int(np.floor(duration / 60)) % 60) + \
            " min " + str(int(np.floor(duration)) % 60) + " sec"
        self._print(string_tools.cbox(["finished wcc calculation" + "\ntime: "
                                      + duration_string,'CONVERCENGE REPORT\n------------------\n\n' + str(self._log)]) + '\n')

    # has to be below wcc_calc because _validate_kwargs needs access to
    # wcc_calc.__doc__
    @_validate_kwargs(target=wcc_calc)
    def __init__(self,
                 m_handle,
                 edge_function,
                 **kwargs):
        self._m_handle = m_handle
        self._edge_function = edge_function
        self._defaults = {'no_iter': False,
                          'no_neighbour_check': False,
                          'no_move_check': False,
                          'wcc_tol': 1e-2,
                          'gap_tol': 2e-2,
                          'move_check_factor': 0.5,
                          'iterator': range(8, 27, 2),
                          'min_neighbour_dist': 0.01,
                          'use_pickle': True,
                          'pickle_file': 'res_pickle.txt',
                          'num_strings': 11,
                          'verbose': True}
        self._defaults.update(kwargs)
        self._current = copy.deepcopy(self._defaults)
        self._log = logger.Logger(logger.ConvFail('string iteration', 't = {}, k = {}'),
                                   logger.ConvFail('neighbour check',
                                    'between t = {}, k = {}\n    and t = {}, k = {}'),
                                   logger.ConvFail('movement check',
                                    'between t = {}, k = {}\n    and t = {}, k = {}'))

    def log(self):
        """
        Returns the convergence report for the wcc calculation.
        """
        return str(self._log)

    #-------------------------------------------------------------------#
    #                support functions for wcc                          #
    #-------------------------------------------------------------------#

    # checking distance gap-wcc
    def _check_neighbours(self):
        """
        checks the neighbour conditions, adds a value in k_points when
        they are not fulfilled
        - adds at most one k_point per run
        - returns Boolean: all neighbour conditions fulfilled <=> True
        """
        for i, status in enumerate(self._neighbour_check):
            if not status:
                if self._string_status[i] and self._string_status[i + 1]:
                    neighbour_check, move_check = self._check_single_neighbour(i)
                    if not (neighbour_check and move_check):
                        if not self._add_string(i):
                            t1 = self._t_points[i]
                            t2 = self._t_points[i + 1]
                            k1 = string_tools.fl_to_s(self._edge_function(t1), 6)
                            k2 = string_tools.fl_to_s(self._edge_function(t2), 6)
                            if not neighbour_check:
                                self._log.log('neighbour check', t1, k1, t2, k2)
                            if not move_check:
                                self._log.log('movement check', t1, k1, t2, k2)
                        return False
                else:
                    return False
        return True

    @verbose_prt.dispatcher
    def _check_single_neighbour(self, i):
        """
        Performs the neighbour check and movement check for neighbours at
        i and i + 1 
        """
        neighbour_check = True
        move_check = True
        if not self._current['no_neighbour_check']:
            neighbour_check = self._check_gap_distance(i)
        if not self._current['no_move_check']:
            tolerance = self._current['move_check_factor'] * min(self._gapsize[i], self._gapsize[i + 1])
            move_check = self._convcheck(self._wcc_list[i], self._wcc_list[i + 1], tolerance)
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
            self._kpt_list.insert(i + 1, self._edge_function(self._t_points[i + 1]))
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
            if(min(abs(1 + wcc_val - self._gaps[i]) % 1, abs(1 - wcc_val + self._gaps[i]) % 1) <
                self._current['gap_tol']):
                return False
        return True

    # pickle: save and load
    def save(self):
        """
        Saves the t-points, WCC, gap positions and sizes and Lambda \
        matrices to a pickle file.

        Only works if ``use_pickle == True`` and the path to ``pickle_file`` exists.
        """
        to_save = ['_t_points', '_wcc_list', '_gaps', '_gapsize', '_lambda_list']
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

        if not self._current['no_iter']:
            for N in iterator:
                xold = copy.copy(x)
                x, min_sv, lambda_ = self._trywcc(self._m_handle(t, N))

                # break conditions
                if(self._convcheck(x, xold, self._current['wcc_tol'])):  # success
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

    # wcc convergence functions
    def _convcheck(self, x, y, tol):
        """
        check convergence of wcc from x to y

        depends on: self._current['wcc_tol']
                    roughly corresponds to the total 'movement' in WCC that
                    is tolerated between x and y
        """
        return _convsum(x, y, tol) < 1

    #----------------END OF SUPPORT FUNCTIONS---------------------------#

    def plot(self, shift=0, show=True, axis=None):
        """
        Plots the WCCs and the largest gaps (y-axis) against the t-points \
        (x-axis). 

        :param shift:   Shifts the plot in the y-axis
        :type shift:    float

        :param show:    Toggles showing the plot
        :type show:     bool

        :param ax:      Axis where the plot is drawn
        :type ax:       :mod:`matplotlib` ``axis``

        :returns:       :class:`matplotlib figure` instance (only if \
        ``ax == None``)

        .. note:: This plotting tool is meant as a quick way of \
            looking at the results calculated by Z2Pack, and features \
            very little flexibility. If you wish to create beautiful \
            plots, it is highly recommended to fetch the data with \
            :meth:`.get_res()` and utilize the full power of matplotlib.
        """
        shift = shift % 1
        if not axis:
            return_fig = True
            fig = plt.figure()
            axis = fig.add_subplot(111)
        else:
            return_fig = False
        axis.set_ylim(0, 1)
        axis.set_xlim(-0.01, 1.01)
        axis.plot(self._t_points, [(x + shift) % 1 for x in self._gaps], 'bD')
        # add plots with +/- 1 to ensure periodicity
        axis.plot(self._t_points, [(x + shift) % 1 + 1 for x in self._gaps],
                  'bD')
        axis.plot(self._t_points, [(x + shift) % 1 - 1 for x in self._gaps],
                  'bD')
        for i, kpt in enumerate(self._t_points):
            axis.plot([kpt] * len(self._wcc_list[i]),
                      [(x + shift) % 1 for x in self._wcc_list[i]],
                      "ro")
            # add plots with +/- 1 to ensure periodicity
            axis.plot([kpt] * len(self._wcc_list[i]),
                      [(x + shift) % 1 + 1 for x in self._wcc_list[i]],
                      "ro")
            axis.plot([kpt] * len(self._wcc_list[i]),
                      [(x + shift) % 1 - 1 for x in self._wcc_list[i]],
                      "ro")
        #~ axis.set_xlabel(r'$t$')
        axis.set_xticks([0, 1])
        axis.set_xticklabels(['0', '1'])
        axis.set_ylabel('x', rotation='horizontal')
        axis.set_xlabel('t')
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
        try:
            return {'t_par': self._t_points, 'kpt': self._kpt_list, 'wcc': self._wcc_list, 'gap': self._gaps, 'lambda_': self._lambda_list}
        except (NameError, AttributeError):
            # TODO remove double try - except for a cleaner version to
            # distinguish v1 and v2
            try:
                return {'t_par': self._t_points, 'wcc': self._wcc_list, 'gap': self._gaps, 'lambda_': self._lambda_list}
            except:
                raise RuntimeError('WCC not yet calculated')
        # for a potential Python3 - only version
        #~ except (NameError, AttributeError) as e:
            #~ raise RuntimeError('WCC not yet calculated') from e

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

    def _print(self, string):
        if(self._current['verbose']):
            print(string, end='')
            sys.stdout.flush()

#-------------------------------------------------------------------#
#                CLASS - independent functions                      #
#-------------------------------------------------------------------#

def _convsum(list_a, list_b, epsilon=1e-2, N0=7):
    """
    helper function for _convcheck

    calculates the absolute value of the change in density from list_a
    to list_b, when each WCC corresponds to a triangle of width epsilon
    (and total density = 1)
    """
    N = max(N0 * int(1/(2 * epsilon)), 1)
    val = np.zeros(N)
    for x in list_a:
        index = int(N*x)
        for i in range(0, N0):
            val[(index - i) % N] += 1 - (i/N0)
        for i in range(1, N0):
            val[(index + i) % N] += 1 - (i/N0)
    for x in list_b:
        index = int(N*x)
        for i in range(0, N0):
            val[(index - i) % N] -= 1 - (i/N0)
        for i in range(1, N0):
            val[(index + i) % N] -= 1 - (i/N0)
    return sum(abs(val)) / N0

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


#----------------END CLASS INDEPENDENT FUNCTIONS---------------------#
