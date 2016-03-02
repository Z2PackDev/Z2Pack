#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    02.06.2015 23:27:55 CEST
# File:    _effective_model.py

from __future__ import division, print_function

import numpy as np
import scipy.linalg as la

from .._core._system_base import System as _Z2PackSystem

class System(_Z2PackSystem):
    r"""
    Subclass of :class:`z2pack.System` used for calculating systems with
    effective models

    :param hamilton: A function taking the wavevector ``k`` (``list`` of length 3) as an input and returning the matrix Hamiltonian.
    :type hamilton: function

    :param pos: Positions of the orbitals w.r.t the reduced unit cell.
        Per default, all orbitals are put at the origin.
    :type pos: list

    :param occ: Number of occupied bands. Default: 1/2 the size of the Hamiltonian.
    :type occ: int

    :param hermitian_tol:   Maximum absolute value in the difference between the Hamiltonian and its hermitian conjugate. Use ``hermitian_tol=None`` to deactivate the test entirely.
    :type hermitian_tol:    float

    :param kwargs:      are passed to the :class:`.Surface` constructor via
        :meth:`.surface`, which passes them to :meth:`wcc_calc<.Surface.wcc_calc>`, precedence:
        :meth:`wcc_calc<.Surface.wcc_calc>` > :meth:`.surface` > this (newer kwargs take precedence)
    """
    # RM_V2
    _new_style_system = True

    def __init__(
        self,
        hamilton,
        pos=None,
        occ=None,
        hermitian_tol=1e-6,
        **kwargs
    ):
        self._defaults = kwargs
        self._hamilton = hamilton
        self._hermitian_tol = hermitian_tol

        size = len(self._hamilton([0, 0, 0])) # assuming to be square...
        # add one atom for each orbital in the hamiltonian
        if pos is None:
            self._pos = [np.zeros(3) for _ in range(size)]
        else:
            if len(pos) != size:
                raise ValueError('The number of positions ({0}) does not match the size of the Hamiltonian ({1}).'.format(len(pos), size))
            self._pos = [np.array(p) for p in pos]
        if occ is None:
            self._occ = int(size / 2)
        else:
            self._occ = occ

    def get_eig(self, kpt):
        """
        returns:        eigenstates
        """
        # create k-points for string
        N = len(kpt) - 1
        k_points = kpt[:-1]

        # get eigenvectors corr. to occupied states
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
            idx = idx[:self._occ]
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

        return eigs
