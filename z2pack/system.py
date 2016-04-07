#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 12:03:43 CEST
# File:    _bases.py

r"""Z2Pack can easily be extended to work with different models / systems. The base classes defined here provide the interface to Z2Pack. Of the two classes, :class:`EigenstateSystem` is the more general one and should be preferred if possible."""

import abc

__all__ = ['EigenstateSystem', 'OverlapSystem']

class EigenstateSystem(metaclass=abc.ABCMeta):
    r"""
    Abstract base class for Z2Pack System classes which can provide eigenstates (periodic part :math:`|u_\mathbf{k}\rangle`).
    """

    @abc.abstractmethod
    def get_eig(self, kpt):
        r"""
        Returns the periodic part of the eigenstates at each of the given k-points. The eigenstates are given as columns in a 2D array.

        :param kpt: The list of k-points for which the eigenstates are to be computed.
        :type kpt:  list
        """
        pass

class OverlapSystem(metaclass=abc.ABCMeta):
    r"""
    Abstract base class for Z2Pack System classes which can only provide overlap matrices.
    """

    @abc.abstractmethod
    def get_mmn(self, kpt):
        r"""
        Returns a list of overlap matrices :math:`M_{m,n}` corresponding to the given k-points.

        :param kpt: The list of k-points for which the overlap matrices are to be computed.
        :type kpt:  list
        """
        pass
