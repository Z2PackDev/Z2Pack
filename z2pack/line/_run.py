#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.02.2016 16:04:45 CET
# File:    _run.py

import pickle

import numpy as np

from . import LineResult
from . import EigenstateLineData, OverlapLineData
from ._control import StepCounter, PosCheck

from .._control import (
    StatefulControl,
    IterationControl,
    DataControl,
    ConvergenceControl,
    LineControl
)
from .._helpers import _atomic_save

def run_line(
    *,
    system,
    line,
    iterator=range(8, 27, 2),
    pos_tol=1e-2,
    save_file=None,
    init_result=None,
    load=False,
    load_quiet=True
):
    """
    Wrapper for:
        * getting / disecting old result
        * setting up Controls
            - from old result -> to impl?
            - from input parameters
        * setting up result -> to impl?
        * setting up printing status
        * setting up file backend
    """
    # setting up controls
    controls = []
    controls.append(StepCounter(iterator=iterator))
    if pos_tol is not None:
        controls.append(PosCheck(pos_tol=pos_tol))

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

    return _run_line_impl(*controls, system=system, line=line, save_file=save_file, init_result=init_result)
    

def _run_line_impl(
    *controls,
    system,
    line,
    save_file=None,
    init_result=None
):
    """
    Input parameters:
        * Controls
        * file backend?
    """
    for ctrl in controls:
        if not isinstance(ctrl, LineControl):
            raise ValueError('{} control object is not a LineControl instance.'.format(ctrl.__class__))

    def filter_ctrl(ctrl_type):
        return [ctrl for ctrl in controls if isinstance(ctrl, ctrl_type)]
        
    stateful_ctrl = filter_ctrl(StatefulControl)
    iteration_ctrl = filter_ctrl(IterationControl)
    data_ctrl = filter_ctrl(DataControl)
    convergence_ctrl = filter_ctrl(ConvergenceControl)

    def save():
        if save_file is not None:
            _atomic_save(result, save_file)

    # initialize stateful and data controls from old result
    if init_result is not None:
        for d_ctrl in data_ctrl:
            # not necessary for StatefulControls
            if d_ctrl not in stateful_ctrl:
                d_ctrl.update(init_result.data)
        for s_ctrl in stateful_ctrl:
            try:
                s_ctrl.state = init_result.ctrl_states[s_ctrl.__class__]
            except KeyError:
                pass
        result = LineResult(init_result.data, stateful_ctrl, convergence_ctrl)
        save()

    # Detect which type of System is active
    if hasattr(system, 'get_eig'):
        DataType = EigenstateLineData
        system_fct = system.get_eig
    else:
        DataType = OverlapLineData
        system_fct = system.get_m

    # main loop
    while not all(c_ctrl.converged for c_ctrl in convergence_ctrl):
        run_options = dict()
        for it_ctrl in iteration_ctrl:
            try:
                run_options.update(next(it_ctrl))
            except StopIteration:
                # TODO: report
                return result

        data = DataType(system_fct(
            list(line(k) for k in np.linspace(0., 1., run_options['num_steps']))
        ))

        for d_ctrl in data_ctrl:
            d_ctrl.update(data)

        result = LineResult(data, stateful_ctrl, convergence_ctrl)
        save()

    return result
