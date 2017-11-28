"""Defines the data container for line calculations."""

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

    def __get__(self, instance, owner):  # pylint: disable=missing-docstring
        if not instance:
            return None

        value = self.method(instance)

        with change_lock(instance, 'none'):
            setattr(instance, self.method.__name__, value)
        return value


@export
class WccLineData(metaclass=ConstLocker):
    """Data container for a line constructed directly from the WCC, or from the overlap matrices via the :meth:`from_overlaps` method. The following attributes and properties can be accessed:

    * ``wcc`` : A list of Wannier charge centers.
    * ``pol`` : The total polarization (sum of WCC) along the line.
    * ``gap_pos`` : The position of the largest gap between any two WCC.
    * ``gap_size``: The size of the largest gap between any two WCC.

    .. note::

        The WCC are given in reduced coordinates, which means the possible values range from 0 to 1. The same is true for all values derived from the WCC.

    """

    def __init__(self, wcc):
        self.wcc = wcc

    @classmethod
    def from_overlaps(cls, overlaps):
        r"""Creates a :class:`OverlapLineData` object from a list containing the overlap matrices :math:`M_{m,n}^{\mathbf{k}, \mathbf{k+b}} = \langle u_n^\mathbf{k} | u_m^\mathbf{k+b} \rangle`."""
        return OverlapLineData(overlaps)

    @staticmethod
    def _calculate_wannier_from_wilson(wilson):
        eigs, eigvec = la.eig(wilson)
        wcc = np.array([np.angle(z) / (2 * np.pi) % 1 for z in eigs])
        idx = np.argsort(wcc)
        return list(wcc[idx]), list(eigvec.T[idx])

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
        with change_lock(self, 'none'):
            self.gap_pos, self.gap_size = _gapfind(self.wcc)

    def __getattr__(self, name):
        """Forward to parent class unless for the 'eigenstates' attribute, in which case an AttributeError is raised."""
        if name == 'eigenstates':
            raise AttributeError(
                "This data does not have the 'eigenstates' attribute. This is because the system used does not provide eigenstates, but only overlap matrices. The functionality which resulted in this error can be used only for systems providing eigenstates."
            )
        return super().__getattribute__(name)


@export
class OverlapLineData(WccLineData):
    r"""
    Data container for Line Data constructred from overlap matrices. This has all attributes that :class:`WccLineData` has, and the following additional ones:

    * ``overlaps`` : A list containing the overlap matrix for each step of k-points, as numpy array.
    * ``wilson`` : An array containing the Wilson loop (product of overlap matrices) for the line. The Wilson loop is given in the basis of the eigenstates at the start / end of the line.
    * ``wilson_eigenstates`` : Eigenstates of the Wilson loop, given as a list of 1D - arrays.
    * ``symm_eigvals: List of symmetry eigenvalues
    * ``projectors: All projector matrices A^k (as defined in paper) for a fixed symmetry eigenvalue passed as a parameter.


    Input parameters:
    :param data: data can be either a list containing 
    """

    def __init__(self, overlaps, dmn=None):  # pylint: disable=super-init-not-called

        self.overlaps = [np.array(o, dtype=complex) for o in overlaps]
        if dmn is None:
            self.dmn = None
        else:
            self.dmn = [np.array(d, dtype=complex) for d in dmn]

    def _calculate_wannier(self):
        wcc, wilson_eigenstates = self._calculate_wannier_from_wilson(
            self.wilson
        )
        with change_lock(self, 'none'):
            self.wcc = wcc
            self.wilson_eigenstates = wilson_eigenstates

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

    @_LazyProperty
    def symm_eigvals():
        return np.sort(np.linalg.eig(dmn[0])[0])

    def projectors(self, eigval):
        """Returns eigvals as defined in paper"""
        print("Wrong")
        if self.dmn is None:
            return None

        # Calculate A_k
        pp = []
        for d in self.dmn:
            ew, ev = np.linalg.eig(d)
            if not np.allclose(self.symm_eigvals, np.sort(ew)):
                raise ValueError("dmn matrices have different eigenvalues.")
            # find orthonormal basis in each symmetry eigenspace
            ev_lambda = ev[:, np.where(np.isclose(ew, eigval))[0]]
            q, r = np.linalg.qr(ev_lambda)
            pp.append(q)
        return pp

    def symm_project(self, eigval):
        """Returns a new OverlapLineData object with symmetry projected WCCs"""
        print("Projecting to symmetry eigenvalue:", eigval)
        A_k = self.projectors(eigval)
        print("overlap:", self.overlaps[0])
        print("eigenstates:", self.eigenstates)
        overlaps_projected = [np.dot(np.dot(A_minus, o), A_plus) for o, A_minus, A_plus in zip(self.overlaps, A_k[:-1], A_k[1:])]
        print("projected overlaps:", overlaps_projected[0])
        return OverlapLineData(overlaps_projected)


@export
class EigenstateLineData(OverlapLineData):
    r"""Data container for a line constructed from periodic eigenstates :math:`|u_{n, \mathbf{k}} \rangle`. This has all attributes that :class:`OverlapLineData` has, and the following additional ones:

    * ``eigenstates`` : The eigenstates of the Hamiltonian, given as a list of arrays which contain the eigenstates as row vectors.
    * ``symm_eigvecs``: Symmetry eigenvectors as columns, given in same order as symm_eigvals. It is possible to pass *np.linalg.eig(symmetry) as an argument for both symm_eigvals and symm_eigvecs.
    """

    def __init__(self, eigenstates, symm_eigvals=None, symm_eigvecs=None):  # pylint: disable=super-init-not-called
        self.eigenstates = eigenstates
        self.symm_eigvals = symm_eigvals
        self.symm_eigvecs = symm_eigvecs

    @_LazyProperty
    def overlaps(self):  # pylint: disable=method-hidden
        overlaps = []
        for eig1, eig2 in zip(self.eigenstates, self.eigenstates[1:]):
            overlaps.append(np.dot(np.conjugate(eig1), np.array(eig2).T))
        return overlaps

    def projectors(self, eigval):
        # eigval: which symmetry eigenvalue (by numerical value, not index)
        # returns: list of A^k as defined in paper
        if self.symm_eigvals is None:
            return None
        ind = np.where(np.isclose(self.symm_eigvals, eigval))[0]
        ev = self.symm_eigvecs[:, ind]
        pp = []
        P = np.dot(ev, ev.conj().T)
        for e in self.eigenstates:
            e = np.array(e).T
            A = np.dot(e.conj().T, la.lu(np.dot(P, e).T)[2].T)
            pp.append(A)
        print("Projector:", pp[0])
        return pp
