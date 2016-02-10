#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    09.02.2016 13:38:55 CET
# File:    line.py

from .bases import ConvergenceControl, IterationControl, LineControl, StatefulControl

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
