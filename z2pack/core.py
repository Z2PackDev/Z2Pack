#!/usr/bin/python3
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


import re
import sys
import time
import copy
import pickle
import decorator
import itertools
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt


#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                           LIBRARY CORE                                #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
class System:
    r"""
    Describes the interface a Z2Pack specialisation must fulfil. Also, it
    defines the :meth:`plane` method, which is used to create :class:`Plane`
    instances.

    :param m_handle_creator: Takes the ``edge_function`` and  ``string_vec`` given to :meth:`plane` and creates an ``m_handle`` s.t. ``m_handle(t, N)`` returns the overlap matrices
    :type m_handle_creator: function

    :param kwargs: Keyword arguments are passed to the :class:`Plane` constructor unless overwritten by kwargs to :func:`plane`
    """

    def __init__(self, m_handle_creator, **kwargs):
        self._defaults = kwargs
        self._m_handle_creator = m_handle_creator

    def plane(self, edge_function=None, string_vec=None, **kwargs):
        r"""
        Creates a :class:`Plane` instance.  The plane's position is
        specified by a function ``edge_function``: :math:`t \in [0, 1]
        \rightarrow \mathbb{R}^3` (or, if you want to stay in the same
        UC, :math:`[0, 1]^3`) connecting a pumping parameter :math:`t`
        to the edge of the plane. The direction along which the plane
        extends from this edge, then, is given by ``string_vec``.

        :param edge_function: Returns the start of the k-point string 
            as function of the pumping parameter t.
        
        :param string_vec: Direction of the individual k-point strings.
            Note that ``string_vec`` must connect equivalent k-points
            (i.e. it must be a reciprocal lattice vector). Typically,
            it is one of ``[1, 0, 0]``, ``[0, 1, 0]``, ``[0, 0, 1]``.
        :type string_vec: list (float)
        
        :param kwargs: Keyword arguments are passed to the :class:`Plane`
            constructor. They take precedence over kwargs from the
            :class:`System` constructor.

        :rtype: :class:`Plane`

        .. note:: All directions / positions are given w.r.t. the
            inverse lattice vectors.
        """
        # updating keyword arguments
        kw_arguments = copy.copy(self._defaults)
        kw_arguments.update(kwargs)

        return Plane(self._m_handle_creator(edge_function, string_vec), edge_function=edge_function, **kw_arguments)



class Plane(object):
    r"""
    Describes a plane (or generalised 2D surface) in reciprocal space 
    for which the Z2 topological invariant is to be calculated. It is
    created by using the :class:`System`'s :meth:`plane()<System.plane>` method.

    A :class:`Plane` instance is the main object used to perform Z2Pack
    tasks like calculating WCC and the Z2 invariant, getting results, plotting
    etc.

    :param m_handle:        Function that returns a list of overlap matrices 
        given the pumping parameter :math:`t` and the number of k-points in
        the string.
    :type m_handle:         function
    
    :param edge_function: Returns the start of the k-point string 
        as function of the pumping parameter t.
    
    :param kwargs: Keyword arguments are passed to the :class:`Plane`
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
        """
        Calculates the Wannier charge centers in the given plane

        * automated convergence in string direction
        * automated check for distance between gap and wcc -> add string
        * automated convergence check w.r.t. movement of the WCC between \
        different k-strings.

        :param no_iter:             Turns the automated iteration of the  \
        number of k-points in a string off ``Default: False``
        :type no_iter:              bool

        :param no_neighbour_check:  Turns the automated check for missing  \
        strings (by distance between gaps and WCCs) off ``Default: False``
        :type no_neighbour_check:   bool

        :param wcc_tol:             Maximum movement of a WCC between two  \
        steps for convergence. ``Default: 1e-2``
        :type wcc_tol:              float

        :param gap_tol:             Smallest tolerated distance between the \
        gap and neighbouring WCCs ``Default: 2e-2``
        :type gap_tol:              float

        :param min_neighbour_dist:  Minimum distance between two strings (no \
        new strings will be added, even if the neighbour check fails). \
        ``Default: 0.01``
        :type min_neighbour_dist:   float

        :param iterator:            Generator for the number of points in \
        a k-point string. The iterator should also take care of the maximum \
        number of iterations. It is needed even when ``no_iter=True``, to \
        provide a starting value. ``Default: range(2, 27, 2)``.

        :param use_pickle:          Toggles using the :mod:`pickle` module \
        for saving ``Default: True``
        :type use_pickle:           bool

        :param pickle_file:     Path to a file where the results are stored using \
        the :py:mod:`pickle` module.
        :type pickle_file:      str

        :param num_strings:         Initial number of strings ``Default: 11``
        :type num_strings:          int

        :param verbose:             Toggles printed output ``Default: True``
        :type verbose:              bool

        :param no_move_check:       Toggles checking the movement of \
        neighbouring wcc. ``Default: False``
        :type no_move_check:        bool

        :param move_check_factor:   Scaling factor for the maximum allowed \
        movement between neighbouring wcc. The factor is multiplied by \
        the size of the largest gap between two wcc (from the two \
        neighbouring strings, the smaller value is chosen). ``Default: 0.5``
        :type move_check_factor:    float

        :returns:                   ``tuple (k_points, wcc, gaps)``, \
        ``k_points`` being the positions of the strings of k-points used in \
        the calculation; ``wcc`` the Wannier charge center positions and \
        ``gaps`` the position of the largest gap, both for each of the \
        k-point strings.
        """
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

        # initial output
        if(self._current['verbose']):
            string = "starting wcc calculation\n\n"
            length = max(len(key) for key in self._current.keys()) + 2
            for key in sorted(self._current.keys()):
                value = str(self._current[key])
                if(len(value) > 48):
                    value = value[:45] + '...'
                string += key.ljust(length) + value + '\n'
            string = string[:-1]
            print(string_tools.cbox(string))

        start_time = time.time()

        # initialising
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
                if(self._current['verbose']):
                    print('skipping neighbour checks')
                break

        # dump results into pickle file
        self.save()

        # output to signal end of wcc calculation
        end_time = time.time()
        duration = end_time - start_time
        duration_string = str(int(np.floor(duration / 3600))) + \
            " h " + str(int(np.floor(duration / 60)) % 60) + \
            " min " + str(int(np.floor(duration)) % 60) + " sec"
        if(self._current['verbose']):
            print(string_tools.cbox("finished wcc calculation" + "\ntime: "
                                    + duration_string))

        return (self._t_points, self._wcc_list, self._gaps)

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

    #~ def __str__(self):
        #~ try:
            #~ text = 'kpts:\n' + str(self._t_points)
            #~ text += '\nwcc:\n' + str(self._wcc_list)
            #~ text += '\ngaps:\n' + str(self._gaps)
            #~ text += '\ninvariant:\n' + str(self.invariant())
            #~ return text
        #~ except AttributeError:
            #~ return super(Plane, self).__str__()

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
            if not(status):
                if(self._string_status[i] and self._string_status[i + 1]):
                    if(self._current['verbose']):
                        print("Checking neighbouring t-points t = " + "%.4f" %
                              self._t_points[i] + " and t = " + "%.4f" %
                              self._t_points[i + 1] + "\n", end="")
                        sys.stdout.flush()
                    passed_check = True
                    if not self._current['no_neighbour_check']:
                        passed_check = passed_check and self._check_single_neighbour(i, i + 1)
                    if not self._current['no_move_check']:
                        tolerance = self._current['move_check_factor'] * min(self._gapsize[i], self._gapsize[i + 1])
                        passed_check = passed_check and self._convcheck(self._wcc_list[i], self._wcc_list[i + 1], tolerance)
                    if(passed_check):
                        if(self._current['verbose']):
                            print("Condition fulfilled\n\n", end="")
                            sys.stdout.flush()
                        self._neighbour_check[i] = True
                    else:
                        if(self._t_points[i + 1] - self._t_points[i] <
                           self._current['min_neighbour_dist']):
                            if(self._current['verbose']):
                                print('Reched minimum distance between ' + 
                                'neighbours, did not converge\n\n', end="")
                                sys.stdout.flush()
                            # convergence failed
                            self._neighbour_check[i] = True
                        else:
                            if(self._current['verbose']):
                                print("Condition not fulfilled\n\n", end="")
                                sys.stdout.flush()
                            # add entries due to additional string
                            self._neighbour_check.insert(i + 1, False)
                            self._string_status.insert(i + 1, False)
                            self._t_points.insert(i + 1, (self._t_points[i] +
                                                  self._t_points[i+1]) / 2)
                            self._kpt_list.insert(i + 1, self._edge_function(self._t_points[i + 1]))
                            self._wcc_list.insert(i + 1, [])
                            self._lambda_list.insert(i + 1, [])
                            self._gaps.insert(i + 1, None)
                            self._gapsize.insert(i + 1, None)
                            # check length of the variables
                            assert(len(self._t_points) - 1 ==
                                   len(self._neighbour_check))
                            assert(len(self._t_points) ==
                                   len(self._string_status) ==
                                   len(self._kpt_list) ==
                                   len(self._wcc_list) ==
                                   len(self._gapsize) ==
                                   len(self._lambda_list)==
                                   len(self._gaps))
                            return False
                else:
                    return False
        return True

    def _check_single_neighbour(self, i, j):
        """
        checks if the gap[i] is too close to any of the WCC in
        wcc_list[j] and vice versa
        should be used with j = i + 1
        """
        return self._check_single_direction(self._wcc_list[j], self._gaps[i])

    def _check_single_direction(self, wcc, gap):
        """
        checks if gap is too close to any of the elements in wcc
        """
        for wcc_val in wcc:
            if(min(abs(1 + wcc_val - gap) % 1, abs(1 - wcc_val + gap) % 1) <
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

        # handle legacy outputs
        # TODO: fill in placeholders for unknown parts
        if not(isinstance(res, dict)):
            if(len(res) < 4):
                res.extend([None] * (4 - len(res)))
            [self._t_points, self._wcc_list, self._gaps, self._lambda_list] = res
            self.save()

        # new version -- if the output is a dict
        # TODO: fill in defaults (hierarchy __dict__ < defaults < res ?)
        else:
            self.__dict__.update(res)
            # handle renaming of k_points => t_points
            try:
                self._t_points = self._k_points
            except AttributeError:
                pass
        

    # calculating one string
    def _getwcc(self, t):
        """
        calculates WCC along a string by increasing the number of steps
        (k-points) along the string until the WCC converge
        """
        # initial output
        if(self._current['verbose']):
            print("calculating string at t = {:.4f}, k = {}".format(t, string_tools.fl_to_s(self._edge_function(t))))
            sys.stdout.flush()

        # get new generator
        iterator, self._current['iterator'] = itertools.tee(
            self._current['iterator'], 2)

        N = next(iterator)
        
        if(self._current['verbose']):
            print('    N = ' + str(N), end='')
            sys.stdout.flush()
        x, min_sv, lambda_ = self._trywcc(self._m_handle(t, N))

        # no iteration
        if(self._current['no_iter']):
            if(self._current['verbose']):
                print('no iteration\n\n', end='')
                sys.stdout.flush()
        # iteration
        else:
            for N in iterator:
                xold = copy.copy(x)
                if(self._current['verbose']):
                    # Output
                    print("    N = " + str(N), end="")
                    sys.stdout.flush()
                x, min_sv, lambda_ = self._trywcc(self._m_handle(t, N))

                # break conditions
                if(self._convcheck(x, xold, self._current['wcc_tol'])):  # success
                    if(self._current['verbose']):
                        print("finished!\n\n", end="")
                        sys.stdout.flush()
                    break
            # iterator ended
            else:
                if(self._current['verbose']):
                    print('iterator ends, failed to converge!\n\n', end='')
                    sys.stdout.flush()
        return sorted(x), lambda_

    def _print_wcc(func):
        """
        decorator to print wcc after a function call (if verbose)
        """
        def inner(*args, **kwargs):
            """
            decorated function
            """
            res = func(*args, **kwargs)
            wcc = sorted(res[0])
            if(args[0]._current['verbose']):
                print(" (" + "%.3f" % res[1] + ")", end='\n        ')
                print('WCC positions: ', end='\n        ')
                print('[', end='')
                line_length = 0
                for val in wcc[:-1]:
                    line_length += len(str(val)) + 2
                    if(line_length > 60):
                        print('', end='\n        ')
                        line_length = len(str(val)) + 2
                    print(val, end=', ')
                line_length += len(str(wcc[-1])) + 2
                if(line_length > 60):
                    print('', end='\n        ')
                print(wcc[-1], end=']\n')
                sys.stdout.flush
            return res
        return inner

    @_print_wcc
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
        if(len(x) != len(y)):
            if(self._current['verbose']):
                print("Warning: consecutive strings don't have the same " + 
                      "amount of WCC")
            return False
        else:
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
        axis.set_ylabel(r'$x$', rotation='horizontal')
        axis.set_xlabel(r'$t$')
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
