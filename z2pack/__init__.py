#!/usr/bin/python3.3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    21.03.2014 11:46:38 CET
# File:    z2pack.py
"""
Core functionality of Z2Pack used for calculating the topoligical \
invariants and Wannier charge centers. The Core library interfaces to \
the different specialisations, which create overlap matrices. \
It contains the classes Z2PackSystem (which acts as hook for the \
specialisations) and Z2PackPlane (responsible for all the calculation / \
plots etc.)
"""

from __future__ import print_function

from .python_tools import string_tools

import re
import sys
import time
import copy
import pickle
import decorator
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt


#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                           LIBRARY CORE                                #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
class Z2PackSystem:
    """
    abstract Base Class for Z2Pack systems (Interface definition)

    :param m_handle_creator: Takes (``string_dir``, ``plane_pos_dir``, \
    ``plane_pos``) and creates an ``m_handle`` s.t. ``m_handle(kx, N)`` \
    returns the overlap matrices
    :type m_handle_creator: function

    :param kwargs: Passed to the :class:`Z2PackPlane` constructor unless\
     overwritten by kwargs to :func:`plane`
    """

    def __init__(self, m_handle_creator, **kwargs):
        self._defaults = kwargs
        self._m_handle_creator = m_handle_creator

    def plane(self, string_dir, plane_pos_dir, plane_pos, **kwargs):
        """
        Creates a :class:`Z2PackPlane` object. The directions are given \
        w.r.t. the inverse lattice vectors.

        :param string_dir: direction of the string of k-points
        :type string_dir: int

        :param plane_pos_dir: index of the reciprocal lattice vector not in \
        the plane
        :type plane_pos_dir: int

        :param plane_pos: position of the plane along ``plane_pos_dir``
        :type plane_pos: float

        :param kwargs: passed to :class:`Z2PackPlane` constructor. Take \
        precedence over kwargs from class:`Z2PackSystem` constructor.

        :rtype: :class:`Z2PackPlane`
        """
        # updating keyword arguments
        kw_arguments = copy.copy(self._defaults)
        kw_arguments.update(kwargs)

        # creating m_handle
        if(string_dir == plane_pos_dir):
            raise ValueError('strings cannot be perpendicular to the plane')

        return Z2PackPlane(self._m_handle_creator(string_dir,
                                                  plane_pos_dir,
                                                  plane_pos),
                           **kw_arguments
                           )


class Z2PackPlane(object):
    """
    Describes a plane in reciprocal space where to calculate the Z2 \
    topological invariant.

    :param m_handle:        Function that returns a list of overlap matrices \
    given the position of the string in the plane ``k`` and the number of \
    k-points on the string ``N``.
    :type m_handle:         function

    :param pickle_file:     Path to a file where the results are stored using \
    the :py:mod:`pickle` module.
    :type pickle_file:      str

    :param kwargs: Are passed to ``wcc_calc``. Kwargs specified in \
    ``wcc_calc`` take precedence
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

        :param no_iter:             Turns the automated iteration of the  \
        number of k-points in a string off
        :type no_iter:              bool

        :param no_neighbour_check:  Turns the automated check for missing  \
        strings (by distance between gaps and WCCs) off
        :type no_neighbour_check:   bool

        :param wcc_tol:             Maximum movement of a WCC between two  \
        steps for convergence
        :type wcc_tol:              float

        :param gap_tol:             Smallest tolerated distance between the \
        gap and neighbouring WCCs
        :type gap_tol:              float

        :param max_iter:            Maximum number of iterations for one string
        :type max_iter:             int

        :param min_neighbour_dist:  Minimum distance between two strings (no \
        new strings will be added, even if the neighbour check fails)
        :type min_neighbour_dist:   float

        :param use_pickle:          Toggles using the :mod:`pickle` module \
        for saving
        :type use_pickle:           bool

        :param num_strings:         Initial number of strings
        :type num_strings:          int

        :param verbose:             Toggles printed output
        :type verbose:              bool

        :returns:                   ``tuple (k_points, wcc, gaps)``, \
        ``k_points`` being the positions of the strings of k-points used in \
        the calculation; ``wcc`` the Wannier charge center positions and \
        ``gaps`` the position of the largest gap, both for each of the \
        k-point strings.
        """
        self._current = copy.copy(self._defaults)
        self._current.update(kwargs)

        # checking num_strings
        if(self._current['num_strings'] < 2):
            raise ValueError("num_strings must be at least 2")

        # initial output
        if(self._current['verbose']):
            string = "starting wcc calculation\n\n"
            length = max(len(key) for key in self._current.keys()) + 2
            for key in sorted(self._current.keys()):
                string += key.ljust(length) + str(self._current[key]) + '\n'
            string = string[:-1]
            print(string_tools.cbox(string))

        start_time = time.time()

        # initialising
        self._k_points = list(np.linspace(0, 0.5, self._current['num_strings'],
                                          endpoint=True))
        self._gaps = [None for i in range(self._current['num_strings'])]
        self._wcc_list = [[] for i in range(self._current['num_strings'])]
        self._neighbour_check = [False for i in
                                 range(self._current['num_strings'] - 1)]
        self._string_status = [False for i in
                               range(self._current['num_strings'])]

        # main calculation part
        # all neighbour checks can be true even if it did not converge!
        # a failed convergence (reaching lower limit) also produces
        # 'true'
        while not (all(self._neighbour_check)):
            for i, kx in enumerate(self._k_points):
                if not(self._string_status[i]):
                    self._wcc_list[i] = self._getwcc(kx)
                    self._gaps[i] = _gapfind(self._wcc_list[i])
                    self._string_status[i] = True
                    self._save()

            if not(self._current['no_neighbour_check']):
                self._check_neighbours()
            else:
                if(self._current['verbose']):
                    print('skipping neighbour checks')
                break

        # dump results into pickle file
        self._save()

        # output to signal end of wcc calculation
        end_time = time.time()
        duration = end_time - start_time
        duration_string = str(int(np.floor(duration / 3600))) + \
            " h " + str(int(np.floor(duration / 60)) % 60) + \
            " min " + str(int(np.floor(duration)) % 60) + " sec"
        if(self._current['verbose']):
            print(string_tools.cbox("finished wcc calculation" + "\ntime: "
                                    + duration_string))

        return (self._k_points, self._wcc_list, self._gaps)

    # has to be below wcc_calc because _validate_kwargs needs access to
    # wcc_calc.__doc__
    @_validate_kwargs(target=wcc_calc)
    def __init__(self,
                 m_handle,
                 pickle_file="res_pickle.txt",
                 **kwargs):
        self._m_handle = m_handle
        self._pickle_file = pickle_file
        self._defaults = {'no_iter': False,
                          'no_neighbour_check': False,
                          'wcc_tol': 1e-2,
                          'gap_tol': 2e-2,
                          'max_iter': 10,
                          'min_neighbour_dist': 0.01,
                          'use_pickle': True,
                          'num_strings': 11,
                          'verbose': True}
        self._defaults.update(kwargs)
        self._current = copy.copy(self._defaults)

    def __str__(self):
        try:
            text = 'kpts:\n' + str(self._k_points)
            text += '\nwcc:\n' + str(self._wcc_list)
            text += '\ngaps:\n' + str(self._gaps)
            text += '\ninvariant:\n' + str(self.invariant())
            return text
        except AttributeError:
            return super(Z2PackPlane, self).__str__()

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
                        print("Checking neighbouring k-points k = " + "%.4f" %
                              self._k_points[i] + " and k = " + "%.4f" %
                              self._k_points[i + 1] + "\n", end="")
                        sys.stdout.flush()
                    if(self._check_single_neighbour(i, i + 1)):
                        if(self._current['verbose']):
                            print("Condition fulfilled\n\n", end="")
                            sys.stdout.flush()
                        self._neighbour_check[i] = True
                    else:
                        if(self._k_points[i + 1] - self._k_points[i] <
                           self._current['min_neighbour_dist']):
                            if(self._current['verbose']):
                                print("Reched minimum distance between \
                                neighbours, did not converge\n\n", end="")
                                sys.stdout.flush()
                            # convergence failed
                            self._neighbour_check[i] = True
                        else:
                            if(self._current['verbose']):
                                print("Condition not fulfilled\n\n", end="")
                                sys.stdout.flush()
                            # add entries to neighbour_check, k_point and
                            # string_status
                            self._neighbour_check.insert(i + 1, False)
                            self._string_status.insert(i + 1, False)
                            self._k_points.insert(i + 1, (self._k_points[i] +
                                                  self._k_points[i+1]) / 2)
                            self._wcc_list.insert(i + 1, [])
                            self._gaps.insert(i + 1, None)
                            # check length of the variables
                            assert(len(self._k_points) == len(self._wcc_list))
                            assert(len(self._k_points) - 1 ==
                                   len(self._neighbour_check))
                            assert(len(self._k_points) ==
                                   len(self._string_status))
                            assert len(self._k_points) == len(self._gaps)
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
            if(min(abs(1 + wcc_val - gap) % 1, abs(1 - gap + wcc_val) % 1) <
               self._current['gap_tol']):
                return False
        return True

    # pickle: save and load
    def _save(self):
        """
        save k_points, wcc and gaps to pickle file
        only works if use_pickle = True & path to pickle_file exists
        """
        if(self._current['use_pickle']):
            fstream = open(self._pickle_file, "wb")
            pickle.dump([self._k_points, self._wcc_list, self._gaps], fstream)
            fstream.close()

    def load(self):
        """
        Loads the data (e.g. from a previous run) from the :mod:`pickle` file.
        """
        fstream = open(self._pickle_file, "rb")
        [self._k_points, self._wcc_list, self._gaps] = pickle.load(fstream)
        fstream.close()

    # calculating one string
    def _getwcc(self, kx):
        """
        calculates WCC along a string by increasing the number of steps
        (k-points) along the string until the WCC converge
        """
        # initial output
        if(self._current['verbose']):
            print("calculating string at kx = " + "%.4f" % kx)
            sys.stdout.flush()

        # first two steps
        N = 8
        niter = 0
        if(self._current['verbose']):
            print('    N = ' + str(N), end='')
            sys.stdout.flush()
        x, min_sv = self._trywcc(self._m_handle(kx, N))

        # no iteration
        if(self._current['no_iter']):
            if(self._current['verbose']):
                print('no iteration\n\n', end='')
                sys.stdout.flush()
        # iteration
        else:
            while(True):
                # larger steps for small min_sv (every second step)
                if(niter % 2 == 1 and min_sv < 0.5):
                    N += 4
                else:
                    N += 2
                xold = copy.copy(x)
                if(self._current['verbose']):
                    # Output
                    print("    N = " + str(N), end="")
                    sys.stdout.flush()
                x, min_sv = self._trywcc(self._m_handle(kx, N))
                niter += 1

                # break conditions
                if(self._convcheck(x, xold)):  # success
                    if(self._current['verbose']):
                        print("finished!\n\n", end="")
                        sys.stdout.flush()
                    break
                if(niter > self._current['max_iter']):  # failure
                    if(self._current['verbose']):
                        print("failed to converge!\n\n", end="")
                        sys.stdout.flush()
                    break
        return sorted(x)

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
        gamma = np.eye(len(all_m[0]))
        min_sv = 1
        for M in all_m:
            [V, E, W] = la.svd(M)
            gamma = np.dot(np.dot(V, W).conjugate().transpose(), gamma)
            min_sv = min(min(E), min_sv)
        # getting the wcc from the eigenvalues of gamma
        [eigs, _] = la.eig(gamma)
        return [(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs], min_sv

    # wcc convergence functions
    def _convcheck(self, x, y):
        """
        check convergence of wcc from x to y

        depends on: self._current['wcc_tol']
                    roughly corresponds to the total 'movement' in WCC that
                    is tolerated between x and y
        """
        if(len(x) != len(y)):
            if(self._current['verbose']):
                print("Warning: consecutive strings don't have the same \
                      amount of WCC")
            return False
        else:
            return _convsum(x, y, self._current['wcc_tol']) < 1

    #----------------END OF SUPPORT FUNCTIONS---------------------------#

    def plot(self, shift=0, show=True, axis=None):
        """
        Plots the WCCs and the largest gaps (y-axis) against the k-points \
        (x-axis).

        :param shift:   Shifts the plot in the y-axis
        :type shift:    float

        :param show:    Toggles showing the plot
        :type show:     bool

        :param ax:      Axis where the plot is drawn
        :type ax:       :mod:`matplotlib` ``axis``

        :returns:       :class:`matplotlib figure` object (only if \
        ``ax == None``)
        """
        shift = shift % 1
        if not axis:
            return_fig = True
            fig = plt.figure()
            axis = fig.add_subplot(111)
        else:
            return_fig = False
        axis.set_ylim(0, 1)
        axis.set_xlim(-0.01, 0.51)
        axis.plot(self._k_points, [(x + shift) % 1 for x in self._gaps], 'bD')
        # add plots with +/- 1 to ensure periodicity
        axis.plot(self._k_points, [(x + shift) % 1 + 1 for x in self._gaps],
                  'bD')
        axis.plot(self._k_points, [(x + shift) % 1 - 1 for x in self._gaps],
                  'bD')
        for i, kpt in enumerate(self._k_points):
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
        axis.set_xlabel(r'$k$')
        axis.set_ylabel(r'$x$', rotation='horizontal')
        if(show):
            plt.show()
        if return_fig:
            return fig

    def get_res(self):
        """
        Returns a ``tuple`` ``(k_points, wcc, gaps)``, ``k_points`` being the \
        positions of the k-point strings used (at which the WCCs were \
        computed), ``wcc`` the WCC positions at each of those positions, and \
        ``gaps`` the positions of the largest gap in each string.
        """
        try:
            return (self._k_points, self._wcc_list, self._gaps)
        except (NameError, AttributeError):
            raise RuntimeError('WCC not yet calculated')
        # for a potential Python3 - only version
        #~ except (NameError, AttributeError) as e:
            #~ raise RuntimeError('WCC not yet calculated') from e

    def invariant(self):
        """
        calculate the Z2 topological invariant
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
    N = N0 * int(1/(2 * epsilon))
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
    return np.copysign(1, np.sin(2*np.pi*(zplus - z)) +
                       np.sin(2*np.pi*(x-zplus)) +
                       np.sin(2*np.pi*(z-x)))


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
    return (wcc[gappos] + gapsize / 2) % 1


#----------------END CLASS INDEPENDENT FUNCTIONS---------------------#

from . import fp
from . import tb

if __name__ == "__main__":
    print("z2pack.py")
