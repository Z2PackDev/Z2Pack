#!/usr/bin/env python
"""Abstract base classes for Control objects, which govern the iteration of Z2Pack runs."""

import abc
import types

__all__ = [
    "ControlContainer",
    "AbstractControl",
    "StatefulControl",
    "DataControl",
    "IterationControl",
    "ConvergenceControl",
    "VolumeControl",
    "SurfaceControl",
    "LineControl",
]


class ControlContainer(types.SimpleNamespace):
    """
    Container for controls, giving simple access to the different types of controls.
    """

    def __init__(
        self, *, controls, categories, valid_type
    ):  # pylint: disable=missing-function-docstring
        self.all = controls
        for ctrl in self.all:
            if not isinstance(ctrl, valid_type):
                raise ValueError(
                    f"Invalid type '{type(ctrl)}' of control, should be '{valid_type}'."
                )

        for name, ctrl_types in categories.items():
            setattr(
                self,
                name,
                [
                    ctrl
                    for ctrl in controls
                    if all(isinstance(ctrl, ctrl_t) for ctrl_t in ctrl_types)
                ],
            )


class AbstractControl(metaclass=abc.ABCMeta):
    """ABC for all control objects. Instances must also have a 'state' attribute to work correctly, which is not enforced by the ABC."""


class StatefulControl(AbstractControl):
    """
    ABC for control objects which have a state. The state must not depend on the given convergence parameters.

    **Concepts:**

    `Constructor:` ``StatefulControl(state=s).state == s`` for any valid state s.

    `State:` The state must be sufficient to uniquely determine the behaviour of the Control, for a given set of input parameters of the constructor. That is, given two equivalent StatefulControl objects, when applying

    .. code :: python

        sc1 = StatefulControl(*args, **kwargs)
        sc2 = StatefulControl(*args, **kwargs)
        ...working with sc1 and/or sc2...
        sc2.state = sc1.state

    ``sc1`` and ``sc2`` are again equivalent. In particular, it is not necessary to use ``update()`` on ``sc2`` in the case of a DataControl.
    """

    @abc.abstractmethod
    def __init__(self, *, state=None, **kwargs):
        super().__init__(**kwargs)

    @property
    @abc.abstractmethod
    def state(self):
        """Returns the state of the Control."""

    @state.setter
    @abc.abstractmethod
    def state(self, value):
        """Sets the state of the Control."""


class DataControl(AbstractControl):
    """ABC for control objects which can be updated with data."""

    @abc.abstractmethod
    def update(self, data):
        pass


class IterationControl(AbstractControl):
    """ABC for iteration control objects. Enforces the existence of ..."""

    @abc.abstractmethod
    def __next__(self):
        pass


class ConvergenceControl(AbstractControl):
    """ABC for convergence tester objects. Enforces the existence of an update method, and the ``converged`` property.
    For LineControl objects, the converged property must be valid (False) also before the first update() call.
    This is not required for SurfaceControl objects."""

    @property
    @abc.abstractmethod
    def converged(self):
        pass


# The only purpose of these subclasses is to distinguish between
# ConvergenceControls which take a VolumeData, SurfaceData or LineData object.


class VolumeControl(AbstractControl):
    """Specializes AbstractControl for Volume objects"""


class SurfaceControl(AbstractControl):
    """Specializes AbstractControl for Surface objects"""


class LineControl(AbstractControl):
    """Specializes AbstractControl for Line objects"""
