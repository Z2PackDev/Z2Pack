#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    squarelattice.py

import sys
sys.path.append("../../../")
import z2pack.tb as tb

# Setting the interaction strength
t1, t2 = (0.2, 0.3)

# Settings used for wcc_calc. Feel free to play around with the different
# options.
settings0 = {'num_strings': 3,
            'pos_check': True,
            'gap_check': False,
            'move_check': False,
            'pos_tol': 1e-2,
            'gap_tol': 2e-2,
            'move_tol': 0.3,
            'iterator': range(8, 27, 2),
            'min_neighbour_dist': 1e-2,
            'use_pickle': True,
            'pickle_file': 'res_pickle.txt',
            'verbose': True
           }
settings1 = {'num_strings': 4,
            'pos_check': True,
            'gap_check': True,
            'move_check': True,
            'pos_tol': 1e-2,
            'gap_tol': 2e-2,
            'move_tol': 0.3,
            'iterator': range(8, 27, 2),
            'min_neighbour_dist': 1e-2,
            'use_pickle': True,
            'pickle_file': 'res_pickle.txt',
            'verbose': True,
            'overwrite': True
           }

H = tb.Hamilton()
H.add_atom(([1, 1], 1), [0, 0, 0])
H.add_atom(([-1, -1], 1), [0.5, 0.5, 0])
H.add_hopping(((0, 0), (1, 1)),
              tb.vectors.combine([0,-1],[0,-1],0),
              t1,
              phase = [1, -1j, 1j, -1])
H.add_hopping(((0, 1), (1, 0)),
              tb.vectors.combine([0,-1],[0,-1],0),
              t1,
              phase = [1, 1j, -1j, -1])
H.add_hopping((((0, 0), (0, 0)),((0, 1), (0, 1))), tb.vectors.neighbours([0,1]), t2)
H.add_hopping((((1, 1), (1, 1)),((1, 0), (1, 0))), tb.vectors.neighbours([0,1]), -t2)

tb_system = tb.System(H)
tb_surface = tb_system.surface(lambda kx: [kx / 2., 0, 0], [0, 1, 0])

tb_surface.wcc_calc(**settings0)
tb_surface.plot()

tb_surface.wcc_calc(**settings1)
tb_surface.plot()

# Printing the results
print("t1: {0}, t2: {1}, Z2 invariant: {2}".format(t1, t2, tb_surface.invariant()))

