#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 18:20:18 CET
# File:    _data.py

import functools

import numpy as np
import scipy.linalg as la
from fsc.export import export
from fsc.locker import ConstLocker, change_lock

from .._utils import _gapfind

class _LazyProperty:
    """Descriptor that replaces itself with the return value of the method when accessed. The class is unlocked before setting the attribute, s.t. it can be used with a Locker type class."""
    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        if not instance:
            return None

        value = self.method(instance)

        with change_lock(instance, 'none'):
            setattr(instance, self.method.__name__, value)
        return value

@export
class WccLineData(metaclass=ConstLocker):
    """Data for a line constructed directly from the WCC, or from the overlap matrices via the ``from_overlaps`` method."""
    def __init__(self, wcc):
        self.wcc = wcc

    @classmethod
    def from_overlaps(cls, overlaps):
        return cls(cls._calculate_wannier(cls._wilson(overlaps))[0])

    @staticmethod
    def _calculate_wannier(wilson):
        eigs, eigvec = la.eig(wilson)
        wcc = np.array([np.angle(z) / (2 * np.pi) % 1 for z in eigs])
        idx = np.argsort(wcc)
        return list(wcc[idx]), list(eigvec.T[idx])

    @staticmethod
    def _wilson(overlaps):
        return functools.reduce(np.dot, overlaps)

    @_LazyProperty
    def pol(self):
        return sum(self.wcc) % 1

    @_LazyProperty
    def gap_pos(self):
        self._calculate_gap()
        return self.gap_pos

    @_LazyProperty
    def gap_size(self):
        self._calculate_gap()
        return self.gap_size

    def _calculate_gap(self):
        with change_lock(self, 'none'):
            self.gap_pos, self.gap_size = _gapfind(self.wcc)

    def __getattr__(self, name):
        if name == 'eigenstates':
            raise AttributeError("This data does not have the 'eigenstates' attribute. This is because the system used does not provide eigenstates, but only overlap matrices. The functionality which resulted in this error can be used only for systems providing eigenstates.")
        return super().__getattribute__(name)

@export
class EigenstateLineData(WccLineData):
    """Data for a line constructed from periodic eigenstates :math:`|u_{n, \vec{k}}\rangle`."""
    def __init__(self, eigenstates):
        self.eigenstates = eigenstates

    @_LazyProperty
    def wilson(self):
        # create overlaps
        overlaps = []

        for eig1, eig2 in zip(self.eigenstates, self.eigenstates[1:]):
            overlaps.append(np.dot(
                np.conjugate(eig1),
                np.array(eig2).T
            ))
        return self._wilson(overlaps)

    @_LazyProperty
    def wcc(self):
        self._calculate_wannier()
        return self.wcc

    @_LazyProperty
    def wilson_eigenstates(self):
        self._calculate_wannier()
        return self.wilson_eigenstates

    def _calculate_wannier(self):
        wcc, wilson_eigenstates = super()._calculate_wannier(self.wilson)
        with change_lock(self, 'none'):
            self.wcc = wcc
            self.wilson_eigenstates = wilson_eigenstates
