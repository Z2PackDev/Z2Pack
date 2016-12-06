#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    09.02.2016 10:08:45 CET
# File:    bases.py

"""Abstract base classesfor Control objects, which govern the iteration of Z2Pack runs."""

import abc


class AbstractControl(metaclass=abc.ABCMeta):
    """ABC for all control objects. Instances must also have a 'state' attribute to work correctly, which is not enforced by the ABC."""
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

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
        pass

    @property
    @abc.abstractmethod
    def state(self):
        """Returns the state of the Control."""
        pass

    @state.setter
    @abc.abstractmethod
    def state(self, value):
        """Sets the state of the Control."""
        pass


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
# ConvergenceControls which take a SurfaceData object and those which take
# a LineData object.
class SurfaceControl(AbstractControl):
    """Specializes AbstractControl for Surface objects"""
    pass

class LineControl(AbstractControl):
    """Specializes AbstractControl for Line objects"""
    pass
