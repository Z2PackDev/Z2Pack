#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.09.2015 11:07:35 CEST
# File:    _run_surface.py

import copy
import time
import pickle
import logging
import contextlib

import numpy as np
from fsc.export import export

from . import _logger
from . import SurfaceData
from . import SurfaceResult
from ._control import MoveCheck, GapCheck

from .._control import (
    LineControl,
    SurfaceControl,
    DataControl,
    StatefulControl,
    ConvergenceControl
)
from .._helpers import _atomic_save
from .._logging_tools import TagAdapter, TagFilter, FilterManager
_logger = TagAdapter(_logger, default_tags=('surface',))

from ..line._run import _run_line_impl
from ..line._control import StepCounter, PosCheck

@export
def run_surface(
        *,
        system,
        surface,
        pos_tol=1e-2,
        gap_tol=2e-2,
        move_tol=0.3,
        iterator=range(8, 27, 2),
        min_neighbour_dist=0.01,
        num_strings=11,
        init_result=None,
        save_file=None,
        load=False,
        load_quiet=True
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

    :returns:                   ``None``. Use :meth:`get_res` and
        :meth:`z2` to get the results.
    """
    _logger.info(locals(), tags=('setup', 'box', 'skip'))

    # setting up controls
    controls = []
    controls.append(StepCounter(iterator=iterator))
    if pos_tol is not None:
        controls.append(PosCheck(pos_tol=pos_tol))
    if move_tol is not None:
        controls.append(MoveCheck(move_tol=move_tol))
    if gap_tol is not None:
        controls.append(GapCheck(gap_tol=gap_tol))

    # setting up init_result
    if init_result is not None:
        if load:
            raise ValueError('Inconsistent input parameters "init_result != None" and "load == True". Cannot decide whether to load result from file or use given result.')
    elif load:
        if save_file is None:
            raise ValueError('Cannot load result from file: No filename given in the "save_file" parameter.')
        try:
            with open(save_file, 'rb') as f:
                init_result = pickle.load(f)
        except IOError as e:
            if not load_quiet:
                raise e

    return _run_surface_impl(
        *controls,
        system=system,
        surface=surface,
        num_strings=num_strings,
        min_neighbour_dist=min_neighbour_dist,
        save_file=save_file,
        init_result=init_result
    )

# filter out LogRecords tagged as 'line_only' in the line.
@FilterManager(logging.getLogger('z2pack.line'), TagFilter(('line_only',)))
def _run_surface_impl(
        *controls,
        system,
        surface,
        num_strings,
        min_neighbour_dist,
        save_file=None,
        init_result=None
):
    r"""Implementation of the surface's run.

    :param controls: Control objects which govern the iteration.
    :type controls: AbstractControl

    :type system: OverlapSystem or EigenvalSystem


    :param surface: Function which defines the surface on which the WCC are calculated.
    """
    start_time = time.time()

    # CONTROL SETUP

    def filter_ctrl(ctrl_type):
        return [ctrl for ctrl in controls if isinstance(ctrl, ctrl_type)]

    line_ctrl = filter_ctrl(LineControl)
    controls = filter_ctrl(SurfaceControl)
    stateful_ctrl = filter_ctrl(StatefulControl)
    data_ctrl = filter_ctrl(DataControl)
    convergence_ctrl = filter_ctrl(ConvergenceControl)

    # HELPER FUNCTIONS

    def get_line(t, init_line_result=None):
        """
        Runs a line calculation and returns its result.
        """
        return _run_line_impl(
            *copy.deepcopy(line_ctrl),
            system=system,
            line=lambda ky: surface(t, ky),
            init_result=init_line_result
        )

    def add_line(t, warn=True):
        """
        Adds a line to the Surface, if it is within min_neighbour_dist of
        the given lines.
        """
        # find whether the line is allowed still
        dist = data.nearest_neighbour_dist(t)
        if dist < min_neighbour_dist:
            if dist == 0:
                _logger.info("Line at t = {} exists already.".format(t))
            else:
                _logger.warn("'min_neighbour_dist' reached: cannot add line at t = {}".format(t))
            return SurfaceResult(data, stateful_ctrl, convergence_ctrl)

        _logger.info('Adding line at t = {}'.format(t))
        data.add_line(t, get_line(t))

        return update_result()

    def update_result():
        """
        Updates all data controls, then creates the result object, saves it to file if necessary and returns the result.
        """
        # update data controls
        for d_ctrl in data_ctrl:
            d_ctrl.update(data)

        # save to file
        result = SurfaceResult(data, stateful_ctrl, convergence_ctrl)

        if save_file is not None:
            _logger.info('Saving surface result to file {}'.format(save_file))
            _atomic_save(result, save_file)
        return result

    def collect_convergence():
        """
        Calculates which neighbours are not converged
        """
        res = np.array([True] * (len(data.lines) - 1))
        for c_ctrl in convergence_ctrl:
            res &= c_ctrl.converged
        _logger.info('Convergence criteria fulfilled for {} of {} neighbouring lines.'.format(sum(res), len(res)))
        return res

    # STEP 1 -- MAKE USE OF INIT_RESULT
    # initialize stateful controls from old result
    if init_result is not None:
        _logger.info("Initializing result from 'init_result'.")
        # make sure old result doesn't change
        init_result = copy.deepcopy(init_result)

        # get states from pre-existing Controls
        for s_ctrl in stateful_ctrl:
            with contextlib.suppress(KeyError):
                s_ctrl.state = init_result.ctrl_states[s_ctrl.__class__]

        data = init_result.data

        # re-run lines with existing result as input
        _logger.info('Re-running existing lines.')
        for line in data.lines:
            line.result = get_line(line.t, line.result)
            update_result()

    else:
        data = SurfaceData()

    # STEP 2 -- PRODUCE REQUIRED STRINGS
    # create lines required by num_strings
    _logger.info("Adding lines required by 'num_strings'.")
    for t in np.linspace(0, 1, num_strings):
        result = add_line(t, warn=False)

    # STEP 3 -- MAIN LOOP
    N = len(data.lines)
    conv = collect_convergence()
    while not all(conv):
        # add lines for all non-converged values
        for i in range(len(conv)):
            if not conv[i]:
                new_t = (data.t[i] + data.t[i + 1]) / 2
                result = add_line(new_t)

        # check if new lines appeared
        N_new = len(data.lines)
        if N == N_new:
            break
        N = N_new
        conv = collect_convergence()

    end_time = time.time()
    _logger.info(end_time - start_time, tags=('box', 'skip-before', 'timing'))
    _logger.info(result.convergence_report, tags=('box', 'convergence_report', 'skip'))
    return result
