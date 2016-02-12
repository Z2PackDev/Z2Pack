#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    09.02.2016 13:38:55 CET
# File:    line.py

from .._control.bases import ConvergenceControl, IterationControl, LineControl, StatefulControl
from ..ptools.locker import Locker
from .._utils import _get_max_move

import six

@six.add_metaclass(Locker)
class StepCounter(IterationControl, StatefulControl, LineControl):
    def __init__(self, *, state=0, iterator):
        self._iterator = iter(iterator)
        self._state = state

    @property
    def state(self):
        return self._state

    def __next__(self):
        new_val = next(self._iterator)
        while new_val <= self._state:
            new_val = next(self._iterator)
        self._state = new_val
        return self._state

@six.add_metaclass(Locker)
class WccConvergence(ConvergenceControl, LineControl, StatefulControl):
    def __init__(self, *, state=None, pos_tol):
        """
        :param state: Contains the maximum movement between the last two iterations, as well as the WCC of the last iteration.
        :type state: dict

        :param pos_tol: Tolerance in the maximum movement of a single WCC position.
        :type pos_tol: float
        """
        self.pos_tol = pos_tol
        if state is not None:
            self.max_move = state['max_move']
            self.last_wcc = state['last_wcc']
        else:
            self.max_move = None
            self.last_wcc = None

    def update(self, data):
        new_wcc = data.wcc
        self.max_move = _get_max_move(new_wcc, self.last_wcc)
        self.last_wcc = new_wcc

    @property
    def converged():
        return self.max_move < self.pos_tol

    @property
    def state(self):
        return dict(
            max_move=self.max_move,
            last_wcc=self.last_wcc
        )
