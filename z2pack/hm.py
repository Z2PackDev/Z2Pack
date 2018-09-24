#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains a class for creating Systems which are described by a Hamiltonian matrix (hm), such as k•p models.
"""

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

    :param convention: The convention used for the Hamiltonian, following the `pythtb formalism <http://www.physics.rutgers.edu/pythtb/_downloads/pythtb-formalism.pdf>`_. Convention 1 means that the eigenvalues of :math:`\mathcal{H}(\mathbf{k})` are wave vectors :math:`\left|\psi_{n\mathbf{k}}\right>`. With convention 2, they are the cell-periodic Bloch functions :math:`\left|u_{n\mathbf{k}}\right>`.
    :type convention: int
    """

    def __init__(
        self,
        hamilton,
        *,
        dim=3,
        pos=None,
        bands=None,
        hermitian_tol=1e-6,
        convention=2
    ):
        self._hamilton = hamilton
        self._hermitian_tol = hermitian_tol
        self._convention = int(convention)
        if self._convention not in {1, 2}:
            raise ValueError(
                "Invalid value '{}' for 'convention', must be either 1 or 2.".
                format(self._convention)
            )

        size = len(self._hamilton([0] * dim))  # assuming to be square...
        # add one atom for each orbital in the hamiltonian
        if pos is None:
            self._pos = [np.zeros(dim) for _ in range(size)]
        else:
            if len(pos) != size:
                raise ValueError(
                    'The number of positions ({0}) does not match the size of the Hamiltonian ({1}).'
                    .format(len(pos), size)
                )
            self._pos = [np.array(p) for p in pos]
        if bands is None:
            bands = size // 2
        if isinstance(bands, int):
            self._bands = list(range(bands))
        else:
            self._bands = bands

    def get_eig(self, kpt):
        __doc__ = super().__doc__  # pylint: disable=redefined-builtin,no-member,unused-variable
        # create k-points for string
        k_points = kpt[:-1]

        # get eigenvectors corr. to the chosen bands
        eigs = []
        for k in k_points:
            ham = self._hamilton(k)
            if self._hermitian_tol is not None:
                diff = la.norm(ham - ham.conjugate().transpose(), ord=np.inf)
                if diff > self._hermitian_tol:
                    raise ValueError(
                        'The Hamiltonian you used is not hermitian, with the maximum difference between the Hamiltonian and its adjoint being {0}. Use the ``hamilton_tol`` input parameter (in the ``tb.Hamilton`` constructor; currently {1}) to set the sensitivity of this test or turn it off completely (``hamilton_tol=None``).'
                        .format(diff, self._hermitian_tol)
                    )
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

        for i, k in enumerate(kpt[:-1]):
            if self._convention == 2:
                # normalize phases to get u instead of phi
                eigs[i] *= np.exp(-2j * np.pi * np.dot(self._pos, k))[:, None]
            eigs[i] = list(eigs[i].T)

        # The last bloch state is the same as the first up to a phase factor
        eigs.append(
            list(
                eigs[0] * np.exp(
                    -2j * np.pi * np.dot(self._pos, kpt[-1] - kpt[0])
                )[None, :]
            )
        )
        return eigs
