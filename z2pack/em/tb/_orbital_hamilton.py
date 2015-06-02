#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    02.06.2015 17:50:33 CEST
# File:    _orbital_hamilton.py

from ._hamilton import Hamilton

class OrbitalHamilton(Hamilton):
    r"""
    Alternative Hamilton class that doesn't require the construction of
    atoms. Instead, it works directly with on-site energies and
    hopping parameters. This class is still in development.
    """
    def __init__(self, on_site, hoppings, positions=None, occ=None):
        self._on_site = on_site
        if len(positions) == len(self._on_site):
            self._positions = [np.array(pos) for pos in positions]
        elif positions is None:
            self._positions = [np.array([0., 0., 0.]) for i in self._on_site]
        else:
            raise ValueError('invalid argument for "positions": must be either None or of the same length as on_site')
        self._hoppings = [[h[0], h[1], np.array(h[2]), h[3]] for h in hoppings]
        if occ is None:
            self._occ = len(on_site)
        else:
            self._occ = occ
    
    def hamiltonian(self, k):
        """
        """
        # setting up the hamiltonian
        H = np.array(np.diag(self._on_site), dtype=complex)
        for i0, i1, G, t in self._hoppings:
            H[i0, i1] += t * np.exp(2j * np.pi * np.dot(G + self._positions[i0] - self._positions[i1], k))
        return H
