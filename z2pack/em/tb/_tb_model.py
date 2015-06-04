#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    02.06.2015 17:50:33 CEST
# File:    _orbital_hamilton.py

from __future__ import division

import copy
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
        self._on_site = np.array(on_site, dtype=float)
        
        # take pos if given, else default to [0., 0., 0.] * number of orbitals
        if pos is None:
            self._pos = [np.array([0., 0., 0.]) for i in self._on_site]
        elif len(pos) == len(self._on_site):
            self._pos = [np.array(pos) for pos in pos]
        else:
            raise ValueError('invalid argument for "pos": must be either None or of the same length as the number of orbitals (on_site)')
            
        # adding hoppings and complex conjugates if required
        self._hop = [[i0, i1, np.array(G, dtype=int), t] for i0, i1, G, t in hop]
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

    def size(self):
        """
        Returns the size of the system (number of orbitals, number of hoppings, number of occupied states) as a ``dict``.
        """
        return dict(orbitals=len(self._on_site), hop=len(self._hop), occ=self._occ)
        
    def print_size():
        """
        Prints the size of the system.
        """
        print('Number of orbitals:\t\t{orbitals}\nNumber of hopping terms:\t {hop}\nNumber of occupied states:\t{occ}'.format(**self.size()))

    def supercell(self, dim, periodic=[True, True, True], passivation=None):
        r"""
        Creates a new tight-binding model which describes a supercell.

        :param dim: The dimensions of the supercell in terms of the previous unit cell. 
        :type dim:  list(int)
        
        :param periodic:    Determines whether periodicity is kept in each crystal direction. If not (entry is ``False``), hopping terms that go across the border of the supercell (in the given direction) are cut.
        :type periodic:     list(bool)
        
        :param passivation: Determines the passivation on the surface layers. It must be a function taking three input variables ``x, y, z``, which are lists ``[bottom, top]`` of booleans indicating whether a given unit cell inside the supercell touches the bottom and top edge in the given direction. The function returns a list of on-site energies (must be the same length as the initial number of orbitals) determining the passivation strength in said unit cell.
        :type passivation:  function
        """
        nx, ny, nz = dim
        dim = np.array(dim, dtype=int)
        per_x, per_y, per_z = periodic

        new_occ = sum(dim) * self._occ

        # the new positions, normalized to the supercell
        new_pos = []
        reduced_pos = [p / dim for p in self._pos]
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    tmp_offset = np.array([i, j, k]) / dim
                    for p in reduced_pos:
                        new_pos.append(tmp_offset + p)
        
        # new hoppings, cutting those that cross the supercell boundary
        # in a non-periodic direction
        new_hop = []
        # full index of an orbital in unit cell at uc_pos
        def full_idx(uc_pos, orbital_idx):
            uc_idx = _pos_to_idx(uc_pos, dim)
            return uc_idx * len(self._on_site) + orbital_idx
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    uc0_pos = np.array([i, j, k], dtype=int)
                    for i0, i1, G, t in self._hop:
                        # new index of orbital 0
                        new_i0 = full_idx(uc0_pos, i0)
                        # position of the uc of orbital 1, not mapped inside supercell
                        full_uc1_pos = uc0_pos + G
                        outside_supercell = [(p < 0) or (p >= d) for p, d in zip(full_uc1_pos, dim)]
                        # test if the hopping should be cut
                        if any([not per and outside for per, outside in zip(periodic, outside_supercell)]):
                            continue
                        else:
                            # G in terms of supercells
                            new_G = np.array(full_uc1_pos / dim, dtype=int)
                            # mapped into the supercell
                            uc1_pos = full_uc1_pos % dim
                            new_i1 = full_idx(uc1_pos, i1)
                            new_hop.append(new_i0, new_i1, new_G, t)

        # new on_site terms, including passivation
        if passivation is None:
            passivation = lambda x, y, z: np.zeros(len(self._on_site))
        new_on_site = []
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    tmp_on_site = copy.deepcopy(self._on_site)
                    tmp_on_site += np.array(passivation(*_edge_detect_pos([i, j, k], dim)), dtype=float)
                    new_on_site.extend(tmp_on_site)

        return Model(on_site=new_on_site, pos=new_pos, hop=new_hop, occ=new_occ, add_cc=False)

    def add_trs(self):
        """
        Creates a new Model which contains the current Model and its time-reversal image.
        """
        new_occ = self._occ * 2
        new_pos = np.vstack([self._pos, self._pos])
        new_on_site = np.hstack([self._on_site, self._on_site])
        new_hop = copy.deepcopy(self._hop)
        idx_offset = len(self._on_site) 
        for i0, i1, G, t in self._hop:
            # here you can either do -G or t.conjugate(), but not both
            new_hop.append([i1 + idx_offset, i0 + idx_offset, -G, t])
        return Model(on_site=new_on_site, pos=new_pos, hop=new_hop, occ=new_occ, add_cc=False)

#-----------------------------------------------------------------------#
#                HELPER FUNCTIONS FOR SUPERCELL                         #
#-----------------------------------------------------------------------#

# helper functions: index <-> position
def _pos_to_idx(pos, dim):
    for p, d in zip(pos, dim):
        if p >= d:
            raise IndexError('pos is out of bounds')
    return ((pos[0] * dim[1]) + pos[1]) * dim[2] + pos[2]

# helper functions: detect edges of the supercell
def _edge_detect_pos(pos, dim):
    for p, d in zip(pos, dim):
        if p >= d:
            raise IndexError('pos is out of bounds')
    edges = [[None] * 2 for i in range(3)]
    for i in range(3):
        edges[i][0] = (pos[i] == 0)
        edges[i][1] = (pos[i] == dim[i] - 1)
    return edges
