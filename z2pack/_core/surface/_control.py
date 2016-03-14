#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 16:30:58 MST
# File:    _control.py

from .._control_base import DataControl, ConvergenceControl, IterationControl, SurfaceControl, StatefulControl
from .._utils import _get_max_move

import numpy as np

class MoveConvergence(DataControl, ConvergenceControl, SurfaceControl):
    def __init__(self, *, move_tol):
        self.move_tol = move_tol
        self._converged = False

    @property
    def converged(self):
        return self._converged

    def update(self, data):
        wcc_list = [line.result.data.wcc for line in data.lines]
        self._converged = [
            _get_max_move(l1, l2) < self.move_tol
            for l1, l2 in zip(wcc_list[:-1], wcc_list[1:])
        ]

class GapConvergence(DataControl, ConvergenceControl, SurfaceControl):
    def __init__(self, *, gap_tol):
        self.gap_tol = gap_tol
        self._converged = False

    @property
    def converged(self):
        return self._converged

    def update(self, data):
        if len(data.lines) > 1:
            wcc_list = [line.result.data.wcc for line in data.lines]
            gap_list = [line.result.data.gap_pos for line in data.lines]
            def get_convergence(wccs, gaps):
                return [
                all(abs(wcc_val - gap) > self.gap_tol for wcc_val in wcc)
                for wcc, gap in zip(wccs, gaps)
                ]
            converged_left = get_convergence(wcc_list[1:], gap_list[:-1])
            converged_right = get_convergence(wcc_list[:-1], gap_list[1:])
            self._converged = list(np.array(converged_left) & np.array(converged_right))
