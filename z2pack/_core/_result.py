#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

from ..ptools.locker import Locker

class Result(metaclass=Locker):
    def __init__(self, data, stateful_ctrl):
        self.data = data
        ctrl_states = dict()
        for s_ctrl in stateful_ctrl:
            ctrl_states[s_ctrl.__class__] = s_ctrl.state
        self.ctrl_states = ctrl_states
