#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

import abc

from fsc.export import export

@export
class Result(metaclass=abc.ABCMeta):
    def __init__(self, data, stateful_ctrl, convergence_ctrl):
        self.data = data
        ctrl_states = dict()
        # save states
        for s_ctrl in stateful_ctrl:
            ctrl_states[s_ctrl.__class__.__name__] = s_ctrl.state
        self.ctrl_states = ctrl_states
        ctrl_convergence = dict()
        # save convergence
        for c_ctrl in convergence_ctrl:
            ctrl_convergence[c_ctrl.__class__.__name__] = c_ctrl.converged
        self.ctrl_convergence = ctrl_convergence

    def __getattr__(self, name):
        if name not in ['data', 'convergence_report']:
            return getattr(self.data, name)
        return super().__getattribute__(name)

    @property
    @abc.abstractmethod
    def convergence_report(self):
        r"""
        Returns a convergence report (as a string) for the result. This report shows whether the convergence options used for calculating this result were satisfied or not.
        """
        pass        
