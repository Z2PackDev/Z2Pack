#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools

from fsc.export import export

from .._control import (
    DataControl,
    ConvergenceControl,
    IterationControl,
    LineControl,
    StatefulControl
)
from .._utils import _get_max_move

@export
class StepCounter(
        IterationControl,
        StatefulControl,
        LineControl
):
    """Counts the number of k-points along the line."""
    def __init__(self, *, iterator):
        self._iterator = iter(iterator)
        self._state = 0

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def __next__(self):
        new_val = next(self._iterator)
        while new_val <= self._state:
            new_val = next(self._iterator)
        self._state = new_val
        return dict(num_steps=self._state)

@export
class ForceFirstUpdate(
        DataControl,
        ConvergenceControl,
        LineControl
):
    """Makes sure at least one update is done, even when the pos_tol argument is not used."""
    def __init__(self):
        self._converged = False

    @property
    def converged(self):
        return self._converged

    def update(self, data):
        self._converged = True

@export
class PosCheck(
        DataControl,
        ConvergenceControl,
        StatefulControl,
        LineControl,
):
    """
    Check the change in position between two line calculations.

    :param pos_tol: Tolerance in the maximum movement of a single WCC position.
    :type pos_tol: float
    """
    def __init__(self, *, pos_tol):
        if not (pos_tol > 0 and pos_tol <= 1):
            raise ValueError('pos_tol must be in (0, 1]')
        self.pos_tol = pos_tol
        self.max_move = None
        self.last_wcc = None

    def update(self, data):
        new_wcc = data.wcc
        if self.last_wcc is not None:
            self.max_move = _get_max_move(new_wcc, self.last_wcc)
        self.last_wcc = new_wcc

    @property
    def converged(self):
        if self.max_move is None:
            return False
        return self.max_move < self.pos_tol

    @property
    def state(self):
        return dict(
            max_move=self.max_move,
            last_wcc=self.last_wcc
        )

    @state.setter
    def state(self, state):
        self.max_move = state['max_move']
        self.last_wcc = state['last_wcc']
