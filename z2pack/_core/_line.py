#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 11:47:40 CEST
# File:    _line.py

from __future__ import division

from ._verbose_prt import dispatcher_line as prt_dispatcher
from ._utils import _convcheck
from ._kwarg_validator import _validate_kwargs

import copy
import pickle
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

    :param kwargs: Keyword arguments are passed to the :meth:`.wcc_calc()`
        method.
    """

    @_validate_kwargs
    @prt_dispatcher
    def wcc_calc(self, **kwargs):
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
        self._current = copy.deepcopy(self._defaults)
        self._current.update(kwargs)
        self._param_check()
        self._wcc, self._lambda, self._converged = self._getwcc()


    # has to be below wcc_calc because _validate_kwargs needs access to
    # wcc_calc.__doc__
    @_validate_kwargs(target=wcc_calc)
    def __init__(self,
                 m_handle,
                 param_fct,
                 **kwargs):
        self._m_handle = m_handle
        self._param_fct = param_fct
        self._defaults = {'pos_tol': 1e-2,
                          'iterator': range(8, 27, 2),
                          'verbose': True}
        self._defaults.update(kwargs)
        self._current = copy.deepcopy(self._defaults)

    #-------------------------------------------------------------------#
    #                support functions for wcc                          #
    #-------------------------------------------------------------------#
    def _param_check(self):
        """
        Checks the current parameters and deletes unnecessary ones.
        """
        if self._current['pos_tol'] is None:
            if not(hasattr(self._current['iterator'], '__next__')):
                self._current['iterator'] = iter(self._current['iterator'])
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self._current['iterator'] = [next(self._current['iterator'])]

    @prt_dispatcher
    def _getwcc(self):
        """
        calculates WCC along a string by increasing the number of steps
        (k-points) along the string until the WCC converge
        """
        converged = True

        # get new generator
        iterator, self._current['iterator'] = itertools.tee(
            self._current['iterator'], 2)

        N = next(iterator)
        x, min_sv, lambda_ = self._trywcc(self._get_m(N))

        if self._current['pos_tol'] is not None:
            for N in iterator:
                xold = copy.copy(x)
                x, min_sv, lambda_ = self._trywcc(self._get_m(N))

                # break conditions
                if(_convcheck(x, xold, self._current['pos_tol'])):  # success
                    break
            # iterator ended
            else:
                converged = False
        return sorted(x), lambda_, converged

    @prt_dispatcher
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
        Returns a ``dict`` with the following keys: ``wcc``, the WCC positions and 
        ``lambda_``, the list of Lambda matrices.
        """
        return {'wcc': self._wcc, 'lambda': self._lambda, 'converged': self._converged}

