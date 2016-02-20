#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 16:40:23 MST
# File:    ctrl_base_tester.py

import pytest
import z2pack
from z2pack._core._control_base import (
    AbstractControl,
    IterationControl,
    DataControl,
    StatefulControl,
    ConvergenceControl
)

@pytest.fixture
def test_ctrl_base():
    def inner(ctrl):
        assert issubclass(ctrl, AbstractControl)
        if hasattr(ctrl, 'converged'):
            assert issubclass(ctrl, ConvergenceControl)
        if hasattr(ctrl, 'state'):
            assert issubclass(ctrl, StatefulControl)
        if hasattr(ctrl, 'update'):
            assert issubclass(ctrl, DataControl)
        if hasattr(ctrl, '__next__'):
            assert issubclass(ctrl, IterationControl)
    return inner
