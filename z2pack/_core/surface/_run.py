#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.09.2015 11:07:35 CEST
# File:    _run_surface.py

from __future__ import division, print_function

from ._utils import _convcheck, _dist
from ._run_line import run_line
from ._result import SurfaceResult
from ..ptools import logger, string_tools

import sys
import time
import copy
import pickle
import itertools
import numpy as np
import scipy.linalg as la

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
    #~ verbose=True,
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

    :param overwrite:           Toggles whether existing data should be
        overwritten or used to re-start a run.
    :type overwrite:            bool

    :returns:                   ``None``. Use :meth:`get_res` and
        :meth:`z2` to get the results.
    """
    return _RunSurfaceImpl(**locals()).run()

def _run_surface_impl(
    *controls,
    system,
    line,
    num_strings,
    min_neighbour_dist,
    save_file=None,
    init_result=None
):

    def filter_ctrl(ctrl_type):
        return [ctrl for ctrl in controls if isinstance(ctrl, ctrl_type)]

    line_ctrl = filter_ctrl(LineControl)
    controls = filter_ctrl(SurfaceControl)    
    stateful_ctrl = filter_ctrl(StatefulControl)
    iteration_ctrl = filter_ctrl(IterationControl)
    data_ctrl = filter_ctrl(DataControl)
    convergence_ctrl = filter_ctrl(ConvergenceControl)

    # initialize stateful controls from old result
    if init_result is not None:
        for s_ctrl in stateful_ctrl:
            try:
                s_ctrl.state = init_result.ctrl_states[s_ctrl.__class__]
            except KeyError:
                pass

    data = SurfaceData()
    def add_line(t, init_line_result=None):
        # find whether the line is allowed still
        if data.nearest_neighbour_dist(t) < min_neighbour_dist:
            return
        line_result = _run_line_impl(
            *copy.deepcopy(line_ctrl),
            system=system,
            line=lambda ky: surface(t, ky),
            init_result=init_line_result
        )
        data.add_line(t, line_result)
    
    # initialize result from old result (re-running lines if necessary) 
    if init_result is not None:
        for line in init_result.lines
            add_line(line.t, line.result)
    # create lines required by num_strings
    for t in np.linspace(0, 1, num_strings):
        add_line(t)

    # update data controls
    for d_ctrl in data_ctrl:
        d_ctrl.update(data)

    def collect_convergence():
        
        
    # main loop
    while not all(
        all(c_ctrl.converged) for c_ctrl in convergence_ctrl
    ):
