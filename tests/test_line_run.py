#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 14:40:53 MST
# File:    test_line_run.py

import z2pack

import pytest
import numpy as np

def test_trivial_run(compare_equal):
    sys = z2pack.em.System(lambda k: np.eye(4))
    line = lambda k: [0, 0, 0]
    result = z2pack.line.run(system=sys, line=line)
    assert result.data.wcc == [0, 0]
    assert result.data.gap_pos == 0.5
    assert result.data.gap_size == 1
    assert result.ctrl_states[z2pack._core.line._control.StepCounter] == 10
    assert result.ctrl_states[z2pack._core.line._control.WccConvergence] == dict(max_move=0, last_wcc=[0, 0])
