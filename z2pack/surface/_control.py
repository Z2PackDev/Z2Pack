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
        self._converged = [
            _get_max_move(l1.wcc, l2.wcc) < self.move_tol * min(l1.gap_size, l2.gap_size)
            for l1, l2 in zip(data.lines[:-1], data.lines[1:])
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
        self._converged = [
            all(abs(w2 - l1.gap_pos) > self.gap_tol * l1.gap_size for w2 in l2.wcc) and
            all(abs(w1 - l2.gap_pos) > self.gap_tol * l2.gap_size for w1 in l1.wcc)
            for l1, l2 in zip(data.lines, data.lines[1:])
        ]
