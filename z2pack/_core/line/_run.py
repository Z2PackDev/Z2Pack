#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.02.2016 16:04:45 CET
# File:    _run.py

from .._control.bases import StatefulControl, IterationControl, DataControl, ConvergenceControl, LineControl
from ._data import LineData
from .._result import Result
from ...ptools.serializer import serializer

def run_line():
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

def _run_line_impl(*controls, line, system, save_file=None, init_result=None):
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
    conv_ctrl = filter_ctrl(ConvergenceControl)

    # initialize stateful and data controls from old result
    if init_result is not None:
        for s_ctrl in stateful_ctrl:
            try:
                s_ctrl.state = init_result.ctrl_states[s_ctrl.__class__]
            except KeyError:
                pass
        for d_ctrl in data_ctrl:
            d_ctrl.update(init_result.data)

    # main loop
    while not all(ctrl.converged for ctrl in conv_ctrl):
        run_options = dict()
        for it_ctrl in iteration_ctrl:
            try:
                run_options.update(next(it_ctrl))
            except StopIteration:
                # TODO: report
                return result

        data = LineData(system.get_m(
            list(line(k) for k in np.linspace(0., 1., options['N']))
        ))

        for d_ctrl in data_control:
            d_ctrl.update(data)

        ctrl_states = dict()
        for s_ctrl in stateful_ctrl:
            ctrl_states[s_ctrl.__class__] = s_ctrl.state
        result = Result(data, ctrl_states)

        # save to file
        if save_file is not None:
            serializer.dump(result, save_file)

    return result
