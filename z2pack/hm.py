#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains a class for creating Systems which are described by a Hamiltonian matrix (hm), such as k•p models.
"""

import itertools

import numpy as np
import scipy.linalg as la
from fsc.export import export

from .system import EigenstateSystem

@export
class System(EigenstateSystem):
    r"""
    This class is used when the system can be explicitly described as a matrix Hamiltonian :math:`\mathcal{H}(\mathbf{k})`.

    :param hamilton: A function taking the wavevector ``k`` (``list`` of length 3) as an input and returning the matrix Hamiltonian.
    :type hamilton: collections.abc.Callable

    :param dim:     Dimension of the system.
    :type dim:      int

    :param pos: Positions of the orbitals w.r.t the reduced unit cell.
        Per default, all orbitals are put at the origin.
    :type pos: list

    :param bands: Specifies either the number of occupied bands (if it is an integer) or which bands should be taken into consideration (if it is a list of indices). If no value is given, half the given bands are considered.
    :type bands: :py:class:`int` or :py:class:`list`

    :param hermitian_tol:   Maximum absolute value in the difference between the Hamiltonian and its hermitian conjugate. Use ``hermitian_tol=None`` to deactivate the test entirely.
    :type hermitian_tol:    float

    :param check_periodic: Evaluate the Hamiltonian at :math:`\{0, 1\}^d` as a simple check if it is periodic. Note that this does not work if the Hamiltonian is written such that the eigenstates acquire a phase when being translated by a lattice vector.
    :type check_periodic: bool
    """
    def __init__(
            self,
            hamilton,
            *,
            dim=3,
            pos=None,
            bands=None,
            hermitian_tol=1e-6,
            check_periodic=False
    ):
        self._hamilton = hamilton
        self._hermitian_tol = hermitian_tol

        if check_periodic:
            k_values = itertools.product([0, 1], repeat=dim)
            k0 = next(k_values)
            H0 = self._hamilton(k0)
            for k in k_values:
                if not np.allclose(H0, self._hamilton(k)):
                    raise ValueError('The given Hamiltonian is not periodic: H(k={}) != H(k={})'.format(k0, k))

        size = len(self._hamilton([0] * dim)) # assuming to be square...
        # add one atom for each orbital in the hamiltonian
        if pos is None:
            self._pos = [np.zeros(dim) for _ in range(size)]
        else:
            if len(pos) != size:
                raise ValueError('The number of positions ({0}) does not match the size of the Hamiltonian ({1}).'.format(len(pos), size))
            self._pos = [np.array(p) for p in pos]
        if bands is None:
            bands = size // 2
        if isinstance(bands, int):
            self._bands = list(range(bands))
        else:
            self._bands = bands

    def get_eig(self, kpt):
        __doc__ = super().__doc__
        # create k-points for string
        k_points = kpt[:-1]

        # get eigenvectors corr. to the chosen bands
        eigs = []
        for k in k_points:
            ham = self._hamilton(k)
            if self._hermitian_tol is not None:
                diff = la.norm(ham - ham.conjugate().transpose(), ord=np.inf)
                if  diff > self._hermitian_tol:
                    raise ValueError('The Hamiltonian you used is not hermitian, with the maximum difference between the Hamiltonian and its adjoint being {0}. Use the ``hamilton_tol`` input parameter (in the ``tb.Hamilton`` constructor; currently {1}) to set the sensitivity of this test or turn it off completely (``hamilton_tol=None``).'.format(diff, self._hermitian_tol))
            eigval, eigvec = la.eigh(ham)
            eigval = np.real(eigval)
            idx = eigval.argsort()

            idx = idx[self._bands]
            idx.sort()
            # take only the lower - energy eigenstates
            eigvec = eigvec[:, idx]

            # cast to complex explicitly to avoid casting error when the phase
            # is complex but the eigenvector itself is not.
            eigs.append(np.array(eigvec, dtype=complex))
        eigs.append(eigs[0])

        # normalize phases to get u instead of phi
        for i, k in enumerate(kpt):
            for j in range(eigs[i].shape[0]):
                eigs[i][j, :] *= np.exp(-2j * np.pi * np.dot(k, self._pos[j]))
            eigs[i] = list(eigs[i].T)

        return eigs
