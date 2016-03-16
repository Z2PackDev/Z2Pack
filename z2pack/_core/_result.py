#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

import abc
from ..ptools.termcolor import color

class Result(metaclass=abc.ABCMeta):
    def __init__(self, data, stateful_ctrl, convergence_ctrl):
        self.data = data
        ctrl_states = dict()
        # save states
        for s_ctrl in stateful_ctrl:
            ctrl_states[s_ctrl.__class__] = s_ctrl.state
        self.ctrl_states = ctrl_states
        ctrl_convergence = dict()
        # save convergence
        for c_ctrl in convergence_ctrl:
            ctrl_convergence[c_ctrl.__class__] = c_ctrl.converged
        self.ctrl_convergence = ctrl_convergence

    def __getattr__(self, key):
        if key != 'data':
            return getattr(self.data, key)
        return super().__getattr__(key)

    @property
    @abc.abstractmethod
    def convergence_report(self):
        pass

class SurfaceResult(Result):
    @property
    def convergence_report(self):
        pass

class LineResult(Result):
    @property
    def convergence_report(self):
        report = []
        for key, value in sorted(self.ctrl_convergence.items(), key=lambda x: x[0].__name__):
            report.append(
                '{0:<20}{color}{1}{nocolor}'.format(
                    key.__name__ + ': ',
                    ('Passed' if value else 'Failed'),
                    color=(color['greenb'] if value else color['redb']),
                    nocolor=color['none']
                )
            )
        return '\n'.join(report)
