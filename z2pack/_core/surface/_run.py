#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.09.2015 11:07:35 CEST
# File:    _run_surface.py

import copy
import pickle

import numpy as np

from ..line._run import _run_line_impl
from ._data import SurfaceData
from .._result import SurfaceResult
from .._control_base import (
    LineControl,
    SurfaceControl,
    DataControl,
    StatefulControl,
    ConvergenceControl
)
from ._control import MoveCheck, GapCheck
from ..line._control import StepCounter, PosCheck

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

    :returns:                   ``None``. Use :meth:`get_res` and
        :meth:`z2` to get the results.
    """

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

def _run_surface_impl(
    *controls,
    system,
    surface,
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
    data_ctrl = filter_ctrl(DataControl)
    convergence_ctrl = filter_ctrl(ConvergenceControl)

    # initialize stateful controls from old result
    if init_result is not None:
        # make sure old result doesn't change
        init_result = copy.deepcopy(init_result)
        for s_ctrl in stateful_ctrl:
            try:
                s_ctrl.state = init_result.ctrl_states[s_ctrl.__class__]
            except KeyError:
                pass

    def get_line(t, init_line_result=None):
        return _run_line_impl(
            *copy.deepcopy(line_ctrl),
            system=system,
            line=lambda ky: surface(t, ky),
            init_result=init_line_result
        )

    # update existing data, without losing any old data
    if init_result is not None:
        for line in init_result.data.lines:
            line.result = get_line(line.t, line.result)
            # save to file
            if save_file is not None:
                with open(save_file, 'wb') as f:
                    pickle.dump(init_result, f, protocol=4)
        data = init_result.data
    else:
        data = SurfaceData()

    def add_line(t):
        """
        Adds a line to the Surface, if it is within min_neighbour_dist of
        the given lines.
        """
        # find whether the line is allowed still
        if data.nearest_neighbour_dist(t) < min_neighbour_dist:
            return SurfaceResult(data, stateful_ctrl, convergence_ctrl)

        data.add_line(t, get_line(t))

        # update data controls
        for d_ctrl in data_ctrl:
            d_ctrl.update(data)

        # save to file
        result = SurfaceResult(data, stateful_ctrl, convergence_ctrl)
        if save_file is not None:
            with open(save_file, 'wb') as f:
                pickle.dump(result, f, protocol=4)

        return result

    # create lines required by num_strings
    for t in np.linspace(0, 1, num_strings):
        result = add_line(t)

    # update data controls
    for d_ctrl in data_ctrl:
        d_ctrl.update(data)

    def collect_convergence():
        """
        Calculates which neighbours are not converged
        """
        res = np.array([True] * (len(data.lines) - 1))
        for c_ctrl in convergence_ctrl:
            res &= c_ctrl.converged
        return res
        
    # main loop
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
    return result
