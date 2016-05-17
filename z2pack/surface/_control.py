#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 16:30:58 MST
# File:    _control.py

import numpy as np

from fsc.export import export

from .._control import (
    DataControl,
    ConvergenceControl,
    IterationControl,
    SurfaceControl,
    StatefulControl
)
from .._utils import _get_max_move

@export
class MoveCheck(DataControl, ConvergenceControl, SurfaceControl):
    def __init__(self, *, move_tol):
        self.move_tol = move_tol
        self._converged = None

    @property
    def converged(self):
        return self._converged

    def update(self, data):
        wcc_list = data.lines
        self._converged = [
            _get_max_move(l1.wcc, l2.wcc) < self.move_tol * min(l1.gap_size, l2.gap_size)
            for l1, l2 in zip(wcc_list[:-1], wcc_list[1:])
        ]

@export
class GapCheck(DataControl, ConvergenceControl, SurfaceControl):
    def __init__(self, *, gap_tol):
        self.gap_tol = gap_tol
        self._converged = None

    @property
    def converged(self):
        return self._converged

    def update(self, data):
        if len(data.lines) > 1:
            wcc_list = data.wcc
            gap_list = data.gap_pos
            gap_size_list = data.gap_size
            def get_convergence(wccs, gaps, gap_sizes):
                return [
                all(abs(wcc_val - gap) > self.gap_tol * gap_size for wcc_val in wcc)
                for wcc, gap, gap_size in zip(wccs, gaps, gap_sizes)
                ]
            gap_size_list = [min(x1, x2) for x1, x2 in zip(gap_size_list, gap_size_list[1:])]
            converged_left = get_convergence(wcc_list[1:], gap_list[:-1], gap_size_list)
            converged_right = get_convergence(wcc_list[:-1], gap_list[1:], gap_size_list)
            self._converged = list(np.array(converged_left) & np.array(converged_right))
