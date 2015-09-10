#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.09.2015 11:07:35 CEST
# File:    _run_surface.py

from __future__ import division, print_function

from ._utils import _convcheck
from ..ptools import logger, string_tools
from ._result import SurfaceResult

import sys
import time
import copy
import itertools
import numpy as np
import scipy.linalg as la

def run_surface(
    system,
    surface,
    pos_tol=1e-2,
    gap_tol=2e-2,
    move_tol=0.3,
    iterator=range(8, 27, 2),
    min_neighbour_dist=0.01,
    num_strings=11,
    verbose=True,
    result=None,
    pfile=None,
    overwrite=False,
    werr=True,
):
    r"""
    TODO: fix
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
    return _RunSurfaceImpl(**locals()).run()

class _RunSurfaceImpl(object):
    def __init__(self, system, surface, **kwargs):
        # this is all sequential, but split into sub-functions for
        # a better overview
        # ---- SYSTEM AND SURFACE ----
        self.get_m = lambda N: system.get_m(self._get_kpt(N))
        self.surface = surface
        # ---- KWARGS ----
        self._init_kwargs(kwargs, ignore_kwargs=['result'])
        # ---- NORMALIZE ITERATOR ----
        self._init_iterator()
        # ---- CREATE DESCRIPTOR ----
        self._init_descriptor(system, surface)
        # ---- CREATE RESULT - CHECK DESCRIPTOR CONSISTENCY ----
        self._init_result(kwargs['result'])
        # ---- CONSISTENCY CHECK FOR CONVERGENCE PARAMETERS ----
        self._init_convergence_params()
        # ---- CREATE PRINT_VARS ----
        if self.verbose:
            self._init_print_vars()    
        # ---- CREATE LOGGER ----
        self._init_logger()

#----------------------- INIT SUPPORT FUNCTIONS-------------------------#

    def _init_kwargs(self, kwargs, ignore_kwargs):
        r"""
        automatically parse kwargs except ignore_kwargs into self
        """
        for key, val in kwargs.items():
            if key not in ignore_kwargs:
                setattr(self, key, val)

    def _init_iterator(self):
        r"""
        Normalizes the iterator, cuts it if pos_tol is None.
        """
        if isinstance(self.iterator, int):
            self.iterator = iter([self.iterator])
        if not hasattr(self.iterator, '__next__'): # replace by abc.Iterator
            self.iterator = iter(self.iterator)
        if self.pos_tol is None:
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self.iterator = [next(self.iterator)]
    
    def _init_descriptor(self, system, surface):
        self.descriptor = dict()
        described_objects = [['system', system], ['surface', surface]]
        for name, obj in described_objects:
            try:
                self.descriptor[name] = obj.descriptor
            except AttributeError:
                self.descriptor[name] = None
    
    def _init_result(self, result):
        # try loading result if it does not exist yet
        if (result is None) and (self.pfile is not None) and (not overwrite):
            try:
                with open(self.pfile, 'rb') as f:
                    result = pickle.load(f)
            # pfile doesn't contain a result
            except IOError:
                pass
        # create result
        if result is None:
            result_exists = False
            if not result_exists:
                self.result = SurfaceResult(self.descriptor['surface'])
        # check pre-existing result for consistency
        else:
            if not isinstance(result, SurfaceResult):
                raise TypeError('Invalid type of surface result: {0}, must be SurfaceResult'.format(type(result)))
            if self.descriptor != result.descriptor:
                msg = 'Current surface descriptor {0} does not match pre-existing descriptor {1}'.format(self.descriptor, result.descriptor)
                self._raise_werr(msg)
            self.result = result

    def _init_convergence_params(self):
        if self.num_strings < 2:
            msg = "num_strings must be at least 2"
            self._raise_werr(msg)

        if self.min_neighbour_dist * (self.num_strings - 1) > 1:
            msg = 'The input for \'min_neighbour_dist\' is larger than the spacing between the \'num_strings\' initial strings. This means that not all strings will actually be created. Decrease min_neighbour_dist or num_strings to solve this issue.'
            self._raise_werr(msg)

        if self.pos_tol is None:
            if not hasattr(self.iterator, '__next__'):
                self.iterator = iter(self.iterator)
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self.iterator = [next(self.iterator)]

    def _init_print_vars(self):
        # make into a dict comprehension when Python2.6 support is lifted
        self.print_vars = dict()
        for key in [
            'pos_tol',
            'gap_tol',
            'move_tol',
            'move_tol',
            'min_neighbour_dist',
            'num_strings',
            'verbose',
            'werr',
            'pfile',
        ]:
            self.print_vars[key] = self.__dict__[key]
        iterator, self.iterator = itertools.tee(self.iterator, 2)
        self.print_vars['iterator'] = list(iterator)

    def _init_logger(self):
        self.log = logger.Logger(
        logger.ConvFail('pos check', 't = {0}, k = {1}'),
        logger.ConvFail('gap check',
                        'between t = {0}, k = {1}\n    and t = {2}, k = {3}'),
        logger.ConvFail('move check',
                        'between t = {0}, k = {1}\n    and t = {2}, k = {3}'))

    def _init_vars(self):
        """
        initialization - creating data containers
        """
        self._neighbour_check = [False] * self.result.num_lines
        self._string_status = [False] * self.result.num_lines
        self._t_values = []
        self._insert_lines(np.linspace(0, 1, self.num_strings))

    def _insert_lines(self, t_values):
        """
        Inserts lines (if possible) at the given t values.
        """
        for tval in t_values:
            # add to _t_values and _neighbour_checks
            assert(tval not in self._t_values)
            self._t_values.append(tval)
            self._t_values = sorted(self._t_values)
            self._neighbour_check.insert(self._t_points.index(tval), False)

            #~ # add line to results
            #~ if not self.result.has_line(tval):
                #~ self.result[tval] = LineResult()    

    def _raise_werr(self, msg, err_type=ValueError, w_type=UserWarning, w_stacklevel=3):
        r"""
        Raises a warning or error depending on the ``werr`` parameter.
        """
        if self.werr:
            raise err_type(msg)
        else:
            warnings.warn(msg, w_type, stacklevel=w_stacklevel)

#----------------------- END OF INIT FUNCTIONS -------------------------#

    def run(self):
        self._run_main()
        return self.result

    def _run_main(self):
        while not all(self._neighbour_check):
            # calculate all current t_values
            for t, status in self._t_values:
                if not status:
                    if self.result.has_line(t):
                        # run with result as input
                        self.result[t] = run_line(..., result=self.result[t])
                    else:
                        descriptor = {'system': self.descriptor['system'], 'line': {'surface': self.descriptor['surface'], 't_value': tval= {'system': self.descriptor['system'], 'line': {'surface': self.descriptor['surface'], 't_value': tval}}
                        # TODO: Surface to Line, start line calculation
                        self.result[t] = run_line()

            # neighbour check: find new t-values
            new_t = []
            for i in range(len(self._neighbour_check)):
                # re-check
                if not self._neighbour_check[i]:
                    if self._gap_check(i):
                        if self._move_check(i):
                            self._neighbour_check[i] = True
                            continue # no need to insert t-value

                new_t.append((self._t_values[i] + self._t_values[i + 1]) / 2.)

            # add the new lines
            self._insert_lines(new_t)

    def _save(self, protocol=pickle.HIGHEST_PROTOCOL):
        if self.pfile is not None:
            with open(self.pfile, 'wb') as f:
                pickle.dump(self.result, f)

#-----------------------------------------------------------------------#

    #-------------------------------------------------------------------#
    #                support functions for wcc                          #
    #-------------------------------------------------------------------#
class old(object):
    @prt_dispatcher
    def _init_vars(self):
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

