#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.05.2015 14:51:41 CEST
# File:    _explicit_hamilton.py


from ._tight_binding import Hamilton

class ExplicitHamilton(Hamilton):
    r"""A subclass of :class:`tb.Hamilton` designed for specifying the tight-binding Hamiltonian directly (as a function).

    :param hamiltonian: A function taking the wavevector ``k`` (``list`` of length 3) as an input and returning the matrix Hamiltonian.
    :type hamiltonian: function
    
    :param num_occ: Number of occupied bands.
    :type num_occ: int

    :param positions: Positions of the orbitals w.r.t the reduced unit cell.
        Per default, all orbitals are put at the origin.
    :type positions: list
    """
    def __init__(self, hamiltonian, num_occ, positions=None):
        super(ExplicitHamilton, self).__init__()
        
        size = len(hamiltonian([0, 0, 0])) # assuming to be square...

        # add one atom for each orbital in the hamiltonian
        if positions is None:
            for i in range(size):
                self.add_atom(([0], 1), [0, 0, 0])
        else:
            if len(positions) != size:
                raise ValueError('The number of positions ({0}) does not match the size of the Hamiltonian ({1}).'.format(len(positions), size))
            for pos in positions:
                self.add_atom(([0], 1), pos)

        self._parse_atoms()

        self._num_electrons = num_occ
        self.hamiltonian = hamiltonian
