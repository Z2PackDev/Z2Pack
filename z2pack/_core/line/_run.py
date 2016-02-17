#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.02.2016 16:04:45 CET
# File:    _run.py

from .._controls.bases import StatefulControl, IterationControl, DataControl, ConvergenceControl, LineControl

def _run_line_impl():
    """
    Wrapper for:
        * getting / disecting old result
        * setting up Controls
            - from old result
            - from input parameters
        * setting up printing status
        * setting up file backend
    """

def _run_line_impl(*controls, save_file=None):
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
    conv_ctrl = filter_ctrl(DataControl)

    # main loop
    ...
