#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.02.2016 16:04:45 CET
# File:    _run.py

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
    stateful_ctrl = [ctrl for ctrl in controls if isinstance(ctrl, StatefulControl)]
    iteration_ctrl = ...
    data_ctrl = ...
    conv_ctrl = ...
    ...
    # main loop
