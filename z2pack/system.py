#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Z2Pack can easily be extended to work with different models / systems. The base classes defined here provide the interface to Z2Pack. Of the two classes, :class:`EigenstateSystem` is the more general one and should be preferred if possible."""

import abc

from fsc.export import export


@export
class EigenstateSystem(metaclass=abc.ABCMeta):
    r"""
    Abstract base class for Z2Pack System classes which can provide eigenstates (periodic part :math:`|u_\mathbf{k}\rangle`).
    """

    @abc.abstractmethod
    def get_eig(self, kpt, use_symm=False):
        r"""
        Returns a list of the following objects:

        * The periodic part of the eigenstates at each of the given k-points. The eigenstates are given as columns in a 2D array.
        * The symmetry eigenvalues. If no symmetry is given, this is ``None``.
        * The symmetry eigenvectors. If no symmetry is given, this is ``None``.

        :param kpt: The list of k-points for which the eigenstates are to be computed.
        :type kpt:  list
        """
        pass


@export
class OverlapSystem(metaclass=abc.ABCMeta):
    r"""
    Abstract base class for Z2Pack System classes which can only provide overlap matrices.
    """

    @abc.abstractmethod
    def get_mmn(self, kpt, use_symm=False):
        r"""
        Returns a list of overlap matrices :math:`M_{m,n}` and a list of symmetry matrices :math:`\tilde{d}_{mn}` if use_symm=true corresponding to the given k-points.

        :param kpt: The list of k-points for which the overlap matrices are to be computed.
        :type kpt:  list

        :param use_symm: (optional) If true, a list of symmetry matrices :math:`\tilde{d}_{mn}` is returned in addition to the overlap matrices.
        :type use_symm: bool
        """
        pass
