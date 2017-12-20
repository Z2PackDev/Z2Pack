"""Tests of the StepCounter control."""
# pylint: disable=redefined-outer-name

import pytest

from z2pack.line._control import StepCounter
import z2pack


def test_base(test_ctrl_base):
    test_ctrl_base(StepCounter)
    assert issubclass(StepCounter, z2pack._control.LineControl)  # pylint: disable=protected-access


@pytest.fixture(params=list(range(1, 20)))
def num_steps(request):
    return request.param


def test_step():
    """
    Test that a simple stepcounter produces the correct sequence.
    """
    step_counter = StepCounter(iterator=range(0, 100, 2))
    for step_number in range(1, 50):
        i = next(step_counter)['num_steps']
        assert step_counter.state == i
        assert i == 2 * step_number
    with pytest.raises(StopIteration):
        next(step_counter)


def test_nonzero_start(num_steps):
    """
    Test that starting from a non-zero step number produces the correct sequence.
    """
    step_counter = StepCounter(iterator=range(0, 1000, 3))
    step_counter.state = num_steps
    assert step_counter.state == num_steps
    for step_number in range(1, 20):
        i = next(step_counter)['num_steps']
        assert step_counter.state == i
        assert i == 3 * (step_number + int(num_steps / 3))


def test_stopiteration(num_steps):
    """
    Test that a StopIteration is raised for different StepCounter lengths.
    """
    step_counter = StepCounter(iterator=range(0, 3 * num_steps, 2))
    with pytest.raises(StopIteration):
        while True:
            i = next(step_counter)['num_steps']
            assert step_counter.state == i
    assert i == int((3 * num_steps - 1) / 2) * 2
