#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    02.06.2015 17:50:33 CEST
# File:    _orbital_hamilton.py

from ._hamilton import Hamilton

import numpy as np

class Model(object):
    r"""
    Describes a tight-binding model.
    
    :param on_site: On-site energies of the orbitals.
    :type on_site:  list
    
    :param hop: Hopping terms. Each hopping terms is a list
        [O1, O2, G, t] where O1 and O2 are the indices of the two orbitals
        involved, G is the reciprocal lattice vector indicating the UC
        where O2 is located (if O1 is located in the home UC), and t
        is the hopping strength.
    :type hop: list
    
    :param pos:   Positions of the orbitals. By default (positions = ``None``),
        all orbitals are put at the origin.
    :type pos:    list
    
    :param occ: Number of occupied states. Default: Half the number of orbitals.
    :type occ:  int
    
    :param add_cc:  Determines whether the complex conjugates of the hopping
        parameters are added automatically. Default: ``True``.
    :type add_cc:   bool
    """
    def __init__(self, on_site, hop, pos=None, occ=None, add_cc=True):
        self._on_site = on_site
        
        # take pos if given, else default to [0., 0., 0.] * number of orbitals
        if pos is None:
            self._pos = [np.array([0., 0., 0.]) for i in self._on_site]
        elif len(pos) == len(self._on_site):
            self._pos = [np.array(pos) for pos in pos]
        else:
            raise ValueError('invalid argument for "pos": must be either None or of the same length as the number of orbitals (on_site)')
            
        # adding hoppings and complex conjugates if required
        self._hop = [[i0, i1, np.array(G), t] for i0, i1, G, t in hop]
        if add_cc:
            self._hop.extend([[i1, i0, -np.array(G), t.conjugate()] for i0, i1, G, t in hop])

        # take occ if given, else default to half the number of orbitals
        if occ is None:
            self._occ = int(len(on_site) / 2)
        else:
            self._occ = int(occ)
    
    def hamilton(self, k):
        """
        Creates the Hamiltonian matrix.
        
        :param k:   k-point
        :type k:    list

        :returns:   2D numpy array
        """
        k = np.array(k)
        H = np.array(np.diag(self._on_site), dtype=complex)
        for i0, i1, G, t in self._hop:
            H[i0, i1] += t * np.exp(2j * np.pi * np.dot(G, k))
        return H
