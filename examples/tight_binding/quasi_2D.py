#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    quasi_2D.py

import sys
sys.path.append("../../src/")
import z2pack

if __name__ == "__main__":
    
    tb = z2pack.TbSystem([1, 0, 0], [0, 1, 0], [0, 0, 1])
    
    # create the two atoms
    tb.add_atom(([1, 1], 1), [0, 0, 0])
    tb.add_atom(([-1, -1], 1), [0.5, 0.5, 0])
    
    # coupling strengths
    t1 = 0.2
    t2 = 0.3
    
    # add hopping between different atoms
    tb.add_hopping(((0, 0), (1, 1)), z2pack.TbVectors.combine([0,-1],[0,-1],0), t1, phase = [1, -1j, 1j, -1])
    tb.add_hopping(((0, 1), (1, 0)), z2pack.TbVectors.combine([0,-1],[0,-1],0), t1, phase = [1, 1j, -1j, -1])
    
    # add hopping between neighbouring orbitals of the same type
    tb.add_hopping((((0, 0), (0, 0)),((0, 1), (0, 1))), z2pack.TbVectors.neighbour_uc([0,1]), t2)
    tb.add_hopping((((1, 1), (1, 1)),((1, 0), (1, 0))), z2pack.TbVectors.neighbour_uc([0,1]), -t2)

    # call to Z2Pack
    tb_system = z2pack.TightBinding(tb)
    tb_plane = tb_system.plane(1, 2, 0, pickle_file = './results/quasi_2D.txt')
    tb_plane.wcc_calc(verbose = True, Nstrings=40, no_neighbour_check = True, no_iter = False)
    tb_plane.plot()
    print("invariant: " + str(tb_plane.invariant()))
