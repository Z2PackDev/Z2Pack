#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    09.02.2016 10:08:45 CET
# File:    bases.py

import abc
import six

@six.add_metaclass(abc.ABCMeta)
class AbstractControl:
    """ABC for all control objects. Instances must also have a 'state' attribute to work correctly, which is not enforced by the ABC."""
    @abc.abstractmethod
    def __init__(self, *, **kwargs):
        pass

class StatefulControl(abc.ABCMeta):
    """
        ABC for control objects which have a state.
        Concepts:
            * ``StatefulControl(state=s).state == s`` for any valid state s.
    """
    @abc.abstractmethod
    def __init__(self, *, state=None, **kwargs):
        pass

    @abc.abstractproperty
    def state():
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

class ConvergenceControl(DataControl):
    """ABC for convergence tester objects. Enforces the existence of an update method, and the converged and state properties"""
    @abc.abstractproperty
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
