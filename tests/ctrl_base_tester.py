"""
Fixtures for testing Control classes.
"""

import pytest
from z2pack._control import (
    AbstractControl, IterationControl, DataControl, StatefulControl,
    ConvergenceControl
)


@pytest.fixture
def test_ctrl_base():
    """
    Test that a control class is a subclass of the right abstract classes.
    """

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
