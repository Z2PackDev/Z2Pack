#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.09.2015 17:36:32 CEST
# File:    _run_line.py


from __future__ import division, print_function

from ._utils import _convcheck
from ..ptools import string_tools
from ._result import LineResult

import sys
import time
import copy
import itertools
import numpy as np
import scipy.linalg as la

def run_line(
    system,
    line,
    pos_tol=1e-2,
    iterator=range(8, 27, 2),
    verbose=True,
    result=None,
    werr=True
):
    r"""
    Calculates the Wannier charge centers on the given line.

    * automated convergence in string direction
    
    :param system:  System for which the WCC should be calculated
    :type system:   ``z2pack.System``
    
    :param line:    Line on which the WCC are calculated.
    :type line:     fct

    :param pos_tol:     The maximum movement of a WCC for the iteration w.r.t. the number of k-points in a single string to converge. The iteration can be turned off by setting ``pos_tol=None``.
    :type pos_tol:              float

    :param iterator:            Generator for the number of points in a k-point string. The iterator should also take care of the maximum number of iterations. It is needed even when ``pos_tol=None``, to provide a starting value.
    :type iterator:             Iterable

    :param verbose:             Toggles printed output.
    :type verbose:              bool
    
    :param werr:    Determines whether warnings should raise Errors.
    :type werr:     bool
    """
    impl = _RunLineImpl(
        system=system,
        line=line,
        pos_tol=pos_tol,
        iterator=iterator,
        verbose=verbose,
        result=result,
        werr=werr
    )
    return impl.run()

class _RunLineImpl(object):
    """
    Implementation of the run_line function.
    """
    def __init__(self, system, line, pos_tol, iterator, verbose, result, werr):
        self.get_m = lambda N: system.get_m(self._get_kpt(N))
        self.line = line
        self.pos_tol = pos_tol
        self.iterator = iterator
        self.werr = werr
        if verbose is True:
            self.verbosity = 'full'
        elif verbose is False:
            self.verbosity = 'none'
        elif verbose in ['full', 'reduced', 'none']:
            self.verbosity = verbose
        else:
            raise ValueError('unknown verbosity level {0}'.format(verbose))
            
        # ---- NORMALIZE ITERATOR ----
        if isinstance(self.iterator, int):
            self.iterator = iter([self.iterator])
        if not hasattr(self.iterator, '__next__'): # replace by abc.Iterator
            self.iterator = iter(self.iterator)
        if self.pos_tol is None:
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self.iterator = [next(self.iterator)]
            
        # ---- CREATE DESCRIPTOR ----
        self.descriptor = dict()
        described_objects = [['system', system], ['line', line]]
        for name, obj in described_objects:
            try:
                self.descriptor[name] = obj.descriptor
            except AttributeError:
                self.descriptor[name] = None
                
        # ---- CREATE PRINT_VARS ----
        if self.verbosity == 'full':
            iterator, self.iterator = itertools.tee(self.iterator, 2)
            self.print_vars = {'pos_tol': self.pos_tol, 'iterator': list(iterator), 'verbose': self.verbosity, 'werr': self.werr, 'descriptor': self.descriptor}
        
        # ---- CREATE LineResult ----
        if result is None:
            self.result = LineResult(self.descriptor['line'])
        else:
            if not isinstance(result, LineResult):
                raise TypeError('Invalid type of line result: {0}, must be LineResult'.format(type(result)))
            if self.descriptor != result.descriptor:
                msg = 'Current line descriptor {0} does not match pre-existing descriptor {1}'.format(self.descriptor, result.descriptor)
                if werr:
                    raise ValueError(msg)
                else:
                    warnings.warng(msg)
            self.result = result

    def run(self):
        """
        Calculates the WCC and returns a result object.
        """
        
        if self.verbosity == 'full':
            start_time = time.time()
            string = "Starting WCC calculation\n\n"
            length = max(len(key) for key in self.print_vars.keys()) + 2
            #~ length = 12
            for key, val in sorted(self.print_vars.items()):
                value = str(val)
                if len(value) > 48:
                    value = value[:45] + '...'
                string += key.ljust(length) + value + '\n'
            string = string[:-1]
            print(string_tools.cbox(string))

        # COMPUTATION
        self._run_main()
        assert(hasattr(self.result, 'wcc'))
        assert(hasattr(self.result, 'lambda_'))
        assert(hasattr(self.result, 'num_iter'))
        assert(hasattr(self.result, 'converged'))
        assert(hasattr(self.result, 'max_move'))

        # FINAL OUTPUT
        # reduced & full
        if self.verbosity in ['full', 'reduced']:
            if self.pos_tol is None:
                print('no iteration\n')
            else:
                # check convergence flag
                if self.result.converged:
                    print("finished! ", end='')
                else:
                    print('iterator ends, failed to converge! ', end='')
                if self.result.max_move is not None:
                    print('final wcc movement <= {0:.2g}\n'.format(self.result.max_move))
        # full only
        if self.verbosity == 'full':
            end_time = time.time()
            duration = end_time - start_time
            duration_string = str(int(np.floor(duration / 3600))) + \
                " h " + str(int(np.floor(duration / 60)) % 60) + \
                " min " + str(int(np.floor(duration)) % 60) + " sec"
            if self.result.converged:
                conv_message = 'CONVERGED'
            else:
                conv_message = 'NOT CONVERGED'

            print(
                string_tools.cbox(
                    ["finished wcc calculation: {0}".format(conv_message) + "\ntime: " + duration_string]))
        # OUTPUT
        return self.result
    

    def _run_main(self):
        """
        calculates WCC along a string by increasing the number of steps
        (k-points) along the string until the WCC converge
        """
        # get new generator
        iterator, self.iterator = itertools.tee(self.iterator, 2)
        N = next(iterator)

        if self.pos_tol is None:
            # catch restart, only exact match matters
            if self.result.wcc is not None and self.result.num_iter == N:
                if self.verbosity in ['full', 'reduced']:
                    print('Number of k-points matches previous run. Skipping calculation.')
                return
            else:
                wcc, _, lambda_ = self._trywcc(self.get_m(N))
                converged = True
                max_move = 1.
                num_iter = N
        else:
            # catch restart
            if self.result.wcc is not None:
                # skip if the condition is fulfilled
                if self.result.max_move < self.pos_tol:
                    if self.verbosity in ['full', 'reduced']:
                        print('pos_tol reached in a previous run!')
                    return
                # else fast-forward to N > previous max
                else:
                    while N <= self.result.num_iter:
                        try:
                            N = next(iterator)
                        except StopIteration:
                            converged = False
                            return
                    # re-attach last N to the iterator
                    iterator = itertools.chain([N], iterator)
                    wcc = copy.deepcopy(self.result.wcc)
                    if self.verbosity in ['full', 'reduced']:
                        print('fast-forwarding to N = {0}.'.format(N))
            # no restart
            else:
                wcc, _, lambda_ = self._trywcc(self.get_m(N))

            for num_iter in iterator:
                wcc_old = copy.copy(wcc)
                wcc, _, lambda_ = self._trywcc(self.get_m(num_iter))
                # break conditions
                converged, max_move = _convcheck(wcc, wcc_old, self.pos_tol)
                if converged:  # success
                    break
        self.result.set(wcc=wcc, lambda_=lambda_, converged=converged, max_move=max_move, num_iter=num_iter)

    def _trywcc(self, all_m):
        """
        Calculates the WCC from the MMN matrices
        """

        #--------printout (if verbosity >= reduced)-----------------#
        if self.verbosity in ['full', 'reduced']:
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
        if self.verbosity in ['full', 'reduced']:
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
        return list(self.line(k) for k in np.linspace(0., 1., N + 1))

    #----------------END OF SUPPORT FUNCTIONS---------------------------#

    
