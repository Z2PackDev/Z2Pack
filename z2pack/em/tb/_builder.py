#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    02.06.2015 17:45:11 CEST
# File:    _hamilton.py

from __future__ import division, print_function

import numpy as np

from ._tb_model import Model

class Builder(object):
    """
    A helper tool to create a tight-binding :class:`.Model` .
    """
    def __init__(self):
        self._reset_atoms()

    def _reset_atoms(self):
        """
        Reset the system.
        """
        self._atoms = []
        self._hoppings = []
        self._electrons = 0

    def add_atom(self, orbitals, pos, occ):
        r"""
        Adds an atom to the tight-binding model.

        :param orbitals:    Orbitals of the atom, given as a ``list`` of their
            energies
        :type orbitals:     list

        :param pos:    Position relative to the reciprocal lattice vector
        :type pos:     list of length 3

        :param occ:     Number of electrons in the atom.
        :type occ:      int

        :returns:       Index of the atom
        :rtype:         int
        """

        # check input
        if len(pos) != 3:
            raise ValueError('position must be a list/tuple of length 3')

        # add the atom - store as (orbitals, num_electrons, position)
        self._atoms.append((tuple(orbitals), occ, tuple(pos)))
        # return the index the atom will get
        return len(self._atoms) - 1

    def add_hopping(self, orbital_pairs, rec_lattice_vec,
                    overlap, phase=None, add_cc=True):
        r"""
        Adds a hopping term between orbitals. If the orbitals are not equal,
        the complex conjugate term is also added.

        :param orbital_pairs:       A tuple ``(orbital_1, orbital_2)``, where
            ``orbital_*`` is again a tuple ``(atom_index, orbital_index)``. Can
            also be a list of orbital pairs.

        :param rec_lattice_vec:     Vector connecting unit cells (``list`` of
            length 3), or list of such vectors

        :param overlap:             Strength of the hopping

        :param phase:               Multiplicative factor for the overlap or
            a ``list`` of factors (one for each ``rec_lattice_vec``)

        :param add_cc:       Toggles adding the complex conjugate hopping
            automatically.
        :type add_cc:        bool
        """
        # check if there are multiple orbital pairs
        try:
            orbital_pairs[0][0][0]
            for pair in orbital_pairs:
                self.add_hopping(pair, rec_lattice_vec, overlap, phase)
        except TypeError:
            # check if the orbitals exist
            num_atoms = len(self._atoms)
            if not(orbital_pairs[0][0] < num_atoms and orbital_pairs[1][0] <
                   num_atoms):
                raise ValueError("atom index out of range")
            if not(orbital_pairs[0][1] <
                   len(self._atoms[orbital_pairs[0][0]][0])):
                raise ValueError(
                    "orbital index out of range (orbital_pairs[0])"
                )
            if not(orbital_pairs[1][1] <
                   len(self._atoms[orbital_pairs[1][0]][0])):
                raise ValueError(
                    "orbital index out of range (orbital_pairs[1])"
                )

            # check if there are multiple rec_lattice_vec
            if(hasattr(rec_lattice_vec[0], '__getitem__') and
               hasattr(rec_lattice_vec[0], '__iter__')):
                if phase is None:
                    phase = 1
                if (hasattr(phase, '__getitem__') and
                        hasattr(phase, '__iter__')):
                    if len(phase) == 1:
                        for vec in rec_lattice_vec:
                            self.add_hopping(
                                orbital_pairs,
                                vec,
                                overlap * phase[0]
                            )
                    else:
                        for i, vec in enumerate(rec_lattice_vec):
                            self.add_hopping(
                                orbital_pairs,
                                vec,
                                overlap * phase[i]
                            )
                else:
                    for vec in rec_lattice_vec:
                        self.add_hopping(orbital_pairs, vec, overlap * phase)

            else:
                # check rec_lattice_vec
                if len(rec_lattice_vec) != 3:
                    raise ValueError('length of rec_lattice_vec must be 3')
                for coord in rec_lattice_vec:
                    if not isinstance(coord, int):
                        raise ValueError('rec_lattice_vec must consist \
                                         of integers')

                # add hopping
                rec_lattice_vec = np.array(rec_lattice_vec)
                indices_1 = (orbital_pairs[0][0], orbital_pairs[0][1])
                indices_2 = (orbital_pairs[1][0], orbital_pairs[1][1])
                self._hoppings.append(
                    (
                        overlap,
                        indices_1,
                        indices_2,
                        rec_lattice_vec
                    )
                )
                if add_cc:
                    self._hoppings.append(
                        (
                            overlap.conjugate(),
                            indices_2,
                            indices_1,
                            -rec_lattice_vec
                        )
                    )

    def create(self, add_cc=False):
        r"""
        Creates the :class:`.Model` instance.

        :param add_cc:  Determines whether the complex conjugate of each hopping term should be added automatically. By default, this is handled not withing :meth:`.create()` , but withing :meth:`.add_hopping()` .
        :type add_cc:   bool
        """
        # create conversion from index to orbital/vice versa
        count = 0
        orbital_to_index = []
        orbitals_total = []
        pos_total = []
        occ_total = 0
        for orbitals_atom, occ_atom, pos_atom in self._atoms:
            # number of orbitals - needed for pos and orbital_to_index
            num_orbitals_atom = len(orbitals_atom)
            # do orbitals, occ, pos
            orbitals_total.extend(orbitals_atom)
            occ_total += occ_atom
            pos_total.extend([pos_atom for i in range(num_orbitals_atom)])
            # create orbital_to_index (for hop)
            orbital_to_index.append([count + i for i in range(num_orbitals_atom)])
            count += num_orbitals_atom
        # use orbital_to_index to create hoppings with the correct (orbital) labels
        hop_total = [[orbital_to_index[idx0[0]][idx0[1]], orbital_to_index[idx1[0]][idx1[1]], G, t] for t, idx0, idx1, G in self._hoppings]
        return Model(on_site=orbitals_total, hop=hop_total, pos=pos_total, occ=occ_total, add_cc=add_cc)
