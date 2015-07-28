#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 11:47:40 CEST
# File:    _line.py

from __future__ import division, print_function

from ._utils import _convcheck
from ..ptools import string_tools

import sys
import time
import copy
import itertools
import numpy as np
import scipy.linalg as la

class Line(object):
    r"""
    Describes a line in reciprocal space on which Wannier charge centers are to be calculated. It is created by using the :class:`System`'s :meth:`line()<System.line>` method.

    :param m_handle:        Function that returns a list of overlap matrices
        given the pumping parameter :math:`t` and the number of k-points in
        the string.
    :type m_handle:         function

    :param param_fct: Parametrizes the line as a function of an input parameter :math:`t \in [0, 1]`
    """
    def __init__(self,
                 m_handle,
                 param_fct):
        self.inject(m_handle, param_fct)
        self.wcc = None
        self.lambda_ = None
        self._converged = None
        self._max_move = None
        self._num_iter = None

    def inject(self, m_handle, param_fct):
        r"""
        Injects the ``m_handle`` and ``param_fct``. This can be used for example after unpickling, because m_handle and param_fct cannot be pickled and are thus lost in the pickle/unpickle process.
        """
        self._m_handle = m_handle
        self._param_fct = param_fct

    def __getstate__(self):
        r"""
        Selects which item in the __dict__ should (or can) be saved by pickle. The __init__ function must be called again to make an unpickled Line valid, since m_handle and param_fct cannot be pickled.
        """
        res = {}
        to_save = ['wcc', 'lambda_', '_converged', '_max_move', '_num_iter']
        for key in to_save:
            res[key] = self.__dict__[key]
        return res

    def wcc_calc(self, pos_tol=1e-2, iterator=range(8, 27, 2), verbose=True):
        r"""
        Calculates the Wannier charge centers on the given line.

        * automated convergence in string direction

        :param pos_tol:     The maximum movement of a WCC for the iteration
            w.r.t. the number of k-points in a single string to converge.
            The iteration can be turned off by setting ``pos_tol=None``.
            ``Default: 1e-2``
        :type pos_tol:              float

        :param iterator:            Generator for the number of points in
            a k-point string. The iterator should also take care of the maximum
            number of iterations. It is needed even when ``pos_tol=None``, to
            provide a starting value. ``Default: range(8, 27, 2)``.

        :param verbose:             Toggles printed output ``Default: True``
        :type verbose:              bool

        :returns:                   ``None``
        """
        # could be replaced with inspect call for newer python versions
        self._kwargs = {'pos_tol': pos_tol, 'iterator': iterator, 'verbose': verbose}
        self._param_check()

        # INITIAL OUTPUT
        if self._kwargs['verbose'] == 'full':
            start_time = time.time()
            string = "starting wcc calculation\n\n"
            length = max(len(key) for key in self._kwargs.keys()) + 2
            for key in sorted(self._kwargs.keys()):
                value = str(self._kwargs[key])
                if len(value) > 48:
                    value = value[:45] + '...'
                string += key.ljust(length) + value + '\n'
            string = string[:-1]
            print(string_tools.cbox(string))

        # COMPUTATION
        self._getwcc()

        # FINAL OUTPUT
        # reduced & full
        if self._kwargs['verbose'] in ['full', 'reduced']:
            if self._kwargs['pos_tol'] is None:
                print('no iteration\n')
            else:
                # check convergence flag
                if self._converged:
                    print("finished! ", end='')
                else:
                    print('iterator ends, failed to converge! ', end='')
                if self._max_move is not None:
                    print('final wcc movement <= {0:.2g}\n'.format(self._max_move))
        # full only
        if self._kwargs['verbose'] == 'full':
            end_time = time.time()
            duration = end_time - start_time
            duration_string = str(int(np.floor(duration / 3600))) + \
                " h " + str(int(np.floor(duration / 60)) % 60) + \
                " min " + str(int(np.floor(duration)) % 60) + " sec"
            if self._converged:
                conv_message = 'CONVERGED'
            else:
                conv_message = 'NOT CONVERGED'

            print(
                string_tools.cbox(
                    ["finished wcc calculation: {0}".format(conv_message) + "\ntime: " + duration_string]))
        # CLEANUP
        del self._kwargs

    #-------------------------------------------------------------------#
    #                support functions for wcc                          #
    #-------------------------------------------------------------------#
    def _param_check(self):
        """
        Checks the current parameters and deletes unnecessary ones.
        """
        if self._kwargs['verbose'] is True:
            self._kwargs['verbose'] = 'full'
        elif self._kwargs['verbose'] is False:
            self._kwargs['verbose'] = 'none'
        if not self._kwargs['verbose'] in ['full', 'reduced', 'none']:
            raise ValueError('unknown verbosity level {0}'.format(self._kwargs['verbose']))
        if isinstance(self._kwargs['iterator'], int):
            self._kwargs['iterator'] = iter([self._kwargs['iterator']])
        if not hasattr(self._kwargs['iterator'], '__next__'): # replace by abc.Iterator
            self._kwargs['iterator'] = iter(self._kwargs['iterator'])
        if self._kwargs['pos_tol'] is None:
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self._kwargs['iterator'] = [next(self._kwargs['iterator'])]

    def _getwcc(self):
        """
        calculates WCC along a string by increasing the number of steps
        (k-points) along the string until the WCC converge
        """
        # get new generator
        iterator, self._kwargs['iterator'] = itertools.tee(
            self._kwargs['iterator'], 2)
        N = next(iterator)

        if self._kwargs['pos_tol'] is None:
            # catch restart, only exact match matters
            if self.wcc is not None and self._num_iter == N:
                if self._kwargs['verbose'] in ['full', 'reduced']:
                    print('Number of k-points matches previous run. Skipping calculation.')
                return
            else:
                x, min_sv, lambda_ = self._trywcc(self._get_m(N))
                converged = True
                max_move = 1.
        else:
            # catch restart
            if self.wcc is not None:
                # skip if the condition is fulfilled
                if self._max_move < self._kwargs['pos_tol']:
                    if self._kwargs['verbose'] in ['full', 'reduced']:
                        print('pos_tol reached in a previous run!')
                    return
                # else fast-forward to N > previous max
                else:
                    x = self.wcc
                    while N <= self._num_iter:
                        try:
                            N = next(iterator)
                        except StopIteration:
                            self._converged = False
                            return
                    # re-attach last N to the iterator
                    iterator = itertools.chain([N], iterator)
                    if self._kwargs['verbose'] in ['full', 'reduced']:
                        print('fast-forwarding to N = {0}.'.format(N))
            # no restart
            else:
                x, min_sv, lambda_ = self._trywcc(self._get_m(N))

            for N in iterator:
                xold = copy.copy(x)
                x, min_sv, lambda_ = self._trywcc(self._get_m(N))

                # break conditions
                converged, max_move = _convcheck(x, xold, self._kwargs['pos_tol'])
                if converged:  # success
                    break

        # save results to Line object
        self.wcc = sorted(x)
        self.lambda_ = lambda_
        self._converged = converged
        self._max_move = max_move
        self._num_iter = N

    def _trywcc(self, all_m):
        """
        Calculates the WCC from the MMN matrices
        """

        #--------printout (if verbosity >= reduced)-----------------#
        if self._kwargs['verbose'] in ['full', 'reduced']:
            print('    N = ' + str(len(all_m)), end='')
        #--------main function--------------------------------------#
        lambda_ = np.eye(len(all_m[0]))
        min_sv = 1
        for M in all_m:
            [V, E, W] = la.svd(M)
            lambda_ = np.dot(np.dot(V, W).conjugate().transpose(), lambda_)
            min_sv = min(min(E), min_sv)
        # getting the wcc from the eigenvalues of lambda_
        [eigs, _] = la.eig(lambda_)
        wcc = sorted([(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs])
        #--------printout-------------------------------------------#
        if self._kwargs['verbose'] in ['full', 'reduced']:
            print(' (' + '%.3f' % min_sv + ')\n        ', end='')
            print('WCC positions:\n        ', end='')
            print('[', end='')
            line_length = 0
            for val in wcc[:-1]:
                line_length += len(str(val)) + 2
                if line_length > 60:
                    print('\n        ', end='')
                    line_length = len(str(val)) + 2
                print(str(val) + ', ', end='')
            line_length += len(str(wcc[-1])) + 2
            if line_length > 60:
                print('\n        ', end='')
            print(str(wcc[-1]) + ']')
            sys.stdout.flush()
        #--------end printout---------------------------------------#
        return wcc, min_sv, lambda_

    def _get_kpt(self, N):
        """
        Gets the k-points INCLUDING the last one
        """
        return list(self._param_fct(k) for k in np.linspace(0., 1., N + 1))

    def _get_m(self, N):
        return self._m_handle(self._get_kpt(N))
    #----------------END OF SUPPORT FUNCTIONS---------------------------#

    def get_res(self):
        r"""
        Returns a ``dict`` with the following keys:

        *  ``wcc``: the WCC positions
        * ``converged``: bool indicating whether the WCC calculation converged
        * ``max_move``:  the maximum movement between WCC in the last iteration step
        * ``lambda``: the list of Lambda matrices
        * ``num_iter``: the number of k-points used for the final WCC result
        """
        return {'wcc': self.wcc, 'lambda': self.lambda_, 'converged': self._converged, 'max_move': self._max_move, 'num_iter': self._num_iter}
