#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    squarelattice.py

import z2pack.em.tb as tb
# Setting the interaction strength
t1, t2 = (0.2, 0.3)

# Settings used for wcc_calc. Feel free to play around with the different
# options.
settings = {
            'pos_tol': 1e-6,
            'iterator': range(8, 57, 2),
            'verbose': True
           }

# Creating an empty Hamilton instance
H = tb.Builder()

# Creating the two atoms. The orbitals have opposite energies because
# they are in different sublattices.
H.add_atom([1, 1], [0, 0, 0], 1)
H.add_atom([-1, -1], [0.5, 0.5, 0], 1)

# Add hopping between different atoms
# The first hopping is between the first orbital of the first atom and
# the second orbital of the second atom, (inter-sublattice interation)
H.add_hopping(((0, 0), (1, 0)),
              tb.vectors.combine([0, -1], [0, -1], 0),
              t1,
              phase=[1, -1j, 1j, -1])
# The second interaction is also inter-sublattice, but with the other
# two orbitals. The strength is the same, but the phase is conjugated.
H.add_hopping(((0, 1), (1, 1)),
              tb.vectors.combine([0, -1], [0, -1], 0),
              t1,
              phase=[1, 1j, -1j, -1])

# These are intra-sublattice interactions between neighbouring U.C.
# Sublattice A has positive, sublattice B negative interaction strength
H.add_hopping((((0, 0), (0, 0)), ((0, 1), (0, 1))), tb.vectors.neighbours([0, 1]), t2)
H.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))), tb.vectors.neighbours([0, 1]), -t2)

# Creating the System
tb_system = tb.System(H.create())

# Creating a surface with strings along ky at kz=0
line = tb_system.line(lambda kx: [kx / 2., 0, 0])

# Calculating WCC with standard settings
line.wcc_calc(**settings)

