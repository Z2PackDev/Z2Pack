#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import z2pack
from z2pack._control import (
    AbstractControl, IterationControl, DataControl, StatefulControl,
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
