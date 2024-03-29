"""Defines the data container for line calculations."""

import functools

from fsc.locker import ConstLocker, change_lock
import numpy as np
import scipy.linalg as la

from .._utils import _gapfind

__all__ = [
    "WccLineData",
    "OverlapLineData",
    "EigenstateLineData",
]


class _LazyProperty:
    """Descriptor that replaces itself with the return value of the method when accessed. The class is unlocked before setting the attribute, s.t. it can be used with a Locker type class."""

    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):  # pylint: disable=missing-function-docstring
        if not instance:
            return None

        value = self.method(instance)

        with change_lock(instance, "none"):
            setattr(instance, self.method.__name__, value)
        return value


class WccLineData(metaclass=ConstLocker):
    """Data container for a line constructed directly from the WCC. The following attributes and properties can be accessed:

    * ``wcc`` : A list of Wannier charge centers.
    * ``pol`` : The total polarization (sum of WCC) along the line.
    * ``gap_pos`` : The position of the largest gap between any two WCC.
    * ``gap_size``: The size of the largest gap between any two WCC.

    .. note::

        The WCC are given in reduced coordinates, which means the possible values range from 0 to 1. The same is true for all values derived from the WCC.

    """

    def __init__(self, wcc):
        self.wcc = wcc

    @_LazyProperty
    def pol(self):
        return sum(self.wcc) % 1

    @_LazyProperty
    def gap_pos(self):  # pylint: disable=method-hidden
        self._calculate_gap()
        return self.gap_pos

    @_LazyProperty
    def gap_size(self):  # pylint: disable=method-hidden
        self._calculate_gap()
        return self.gap_size

    def _calculate_gap(self):
        with change_lock(self, "none"):
            self.gap_pos, self.gap_size = _gapfind(self.wcc)

    def __getattr__(self, name):
        """Forward to parent class unless for the 'eigenstates' attribute, in which case an AttributError is raised."""
        if name == "eigenstates":
            raise AttributeError(
                "This data does not have the 'eigenstates' attribute. This is because the system used does not provide eigenstates, but only overlap matrices. The functionality which resulted in this error can be used only for systems providing eigenstates."
            )
        return super().__getattribute__(name)


class OverlapLineData(WccLineData):
    r"""
    Data container for Line Data constructred from overlap matrices. This has all attributes that :class:`WccLineData` has, and the following additional ones:

    * ``overlaps`` : A list containing the overlap matrix for each step of k-points, as numpy array.
    * ``wilson`` : An array containing the Wilson loop (product of overlap matrices) for the line. The Wilson loop is given in the basis of the eigenstates at the start / end of the line.
    * ``wilson_eigenstates`` : Eigenstates of the Wilson loop, given as a list of 1D - arrays.
    """

    def __init__(self, overlaps):  # pylint: disable=super-init-not-called
        self.overlaps = [np.array(o, dtype=complex) for o in overlaps]

    def _calculate_wannier(self):
        """
        Calculates and sets the Wannier charge centers and Wilson loop eigenstates.
        """
        wcc, wilson_eigenstates = self._calculate_wannier_from_wilson(self.wilson)
        with change_lock(self, "none"):
            self.wcc = wcc
            self.wilson_eigenstates = wilson_eigenstates

    @staticmethod
    def _calculate_wannier_from_wilson(wilson):
        """
        Calculates the Wannier charge centers and Wilson loop eigenstates from the Wilson loop.
        """
        eigs, eigvec = la.eig(wilson)
        wcc = np.array([np.angle(z) / (2 * np.pi) % 1 for z in eigs])
        idx = np.argsort(wcc)
        return list(wcc[idx]), list(eigvec.T[idx])

    @_LazyProperty
    def wilson(self):
        """Wilson loop along the line."""
        # create overlaps
        return functools.reduce(np.dot, self.overlaps)

    @_LazyProperty
    def wcc(self):  # pylint: disable=method-hidden
        self._calculate_wannier()
        return self.wcc

    @_LazyProperty
    def wilson_eigenstates(self):  # pylint: disable=method-hidden
        self._calculate_wannier()
        return self.wilson_eigenstates


class EigenstateLineData(OverlapLineData):
    r"""Data container for a line constructed from periodic eigenstates :math:`|u_{n, \mathbf{k}} \rangle`. This has all attributes that :class:`OverlapLineData` has, and the following additional ones:

    * ``eigenstates`` : The eigenstates of the Hamiltonian, given as a list of arrays which contain the eigenstates as row vectors.
    """

    def __init__(self, eigenstates):  # pylint: disable=super-init-not-called
        self.eigenstates = eigenstates

    @_LazyProperty
    def overlaps(self):  # pylint: disable=method-hidden,missing-function-docstring
        overlaps = []
        for eig1, eig2 in zip(self.eigenstates, self.eigenstates[1:]):
            overlaps.append(np.dot(np.conjugate(eig1), np.array(eig2).T))
        return overlaps
