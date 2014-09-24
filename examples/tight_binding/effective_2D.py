#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    effective_2D.py

import sys
sys.path.append("../../src/")
import z2pack

if __name__ == "__main__":
    """
    tb = z2pack.TbSystem([1, 0, 0], [0.5, 0.5, 0], [0, 0, 1])
    tb.add_atom(([1, -1, 1, -1], 2), [0, 0, 0])
    t1 = -0.2
    t2 = 0.3
    tb.add_hopping(1 * t1, (0, 0), (0, 1), [0, 1, 0])
    tb.add_hopping(1j * t1, (0, 0), (0, 1), [-1, 1, 0])
    tb.add_hopping(-1 * t1, (0, 0), (0, 1), [0, -1, 0])
    tb.add_hopping(-1j * t1, (0, 0), (0, 1), [1, -1, 0])
    tb.add_hopping(1 * t1, (0, 2), (0, 3), [0, 1, 0])
    tb.add_hopping(-1j * t1, (0, 2), (0, 3), [-1, 1, 0])
    tb.add_hopping(-1 * t1, (0, 2), (0, 3), [0, -1, 0])
    tb.add_hopping(1j * t1, (0, 2), (0, 3), [1, -1, 0])
    tb.add_hopping(t2, (0, 0), (0, 0), [1, 0, 0])
    tb.add_hopping(t2, (0, 0), (0, 0), [-1, 2, 0])
    tb.add_hopping(t2, (0, 0), (0, 0), [-1, 0, 0])
    tb.add_hopping(t2, (0, 0), (0, 0), [1, -2, 0])
    tb.add_hopping(-t2, (0, 1), (0, 1), [1, 0, 0])
    tb.add_hopping(-t2, (0, 1), (0, 1), [-1, 2, 0])
    tb.add_hopping(-t2, (0, 1), (0, 1), [-1, 0, 0])
    tb.add_hopping(-t2, (0, 1), (0, 1), [1, -2, 0])
    tb.add_hopping(t2, (0, 2), (0, 2), [1, 0, 0])
    tb.add_hopping(t2, (0, 2), (0, 2), [-1, 2, 0])
    tb.add_hopping(t2, (0, 2), (0, 2), [-1, 0, 0])
    tb.add_hopping(t2, (0, 2), (0, 2), [1, -2, 0])
    tb.add_hopping(-t2, (0, 3), (0, 3), [1, 0, 0])
    tb.add_hopping(-t2, (0, 3), (0, 3), [-1, 2, 0])
    tb.add_hopping(-t2, (0, 3), (0, 3), [-1, 0, 0])
    tb.add_hopping(-t2, (0, 3), (0, 3), [1, -2, 0])
    tb.create_hamiltonian()
    print(tb.hamiltonian([0.05, 0, 0]))
    tb_system = z2pack.TightBinding(tb)
    tb_plane = tb_system.plane(1, 0, 0, pickle_file = 'pickle_tb.txt')
    #~ tb_plane.wcc_calc()
    tb_plane.load()
    tb_plane.plot(shift = 0.5)
    print("invariant: " + str(tb_plane.invariant()))
    """
    tb = z2pack.TbSystem([1, 0, 0], [0, 1, 0], [0, 0, 1])
    tb.add_atom(([1, 1], 1), [0, 0, 0])
    tb.add_atom(([-1, -1], 1), [0.5, 0.5, 0])
    t1 = 0.2
    t2 = 0.3
    tb.add_hopping(1 * t1, (0, 0), (1, 1), [0, 0, 0])
    tb.add_hopping(1j * t1, (0, 0), (1, 1), [-1, 0, 0])
    tb.add_hopping(-1 * t1, (0, 0), (1, 1), [-1, -1, 0])
    tb.add_hopping(-1j * t1, (0, 0), (1, 1), [0, -1, 0])
    tb.add_hopping(1 * t1, (0, 1), (1, 0), [0, 0, 0])
    tb.add_hopping(-1j * t1, (0, 1), (1, 0), [-1, 0, 0])
    tb.add_hopping(-1 * t1, (0, 1), (1, 0), [-1, -1, 0])
    tb.add_hopping(1j * t1, (0, 1), (1, 0), [0, -1, 0])
    
    #~ tb.add_hopping(t1, (0, 1), (1, 1), [0, 0, 0])
    #~ tb.add_hopping(t1, (0, 1), (1, 1), [-1, 0, 0])
    #~ tb.add_hopping(t1, (0, 1), (1, 1), [-1, -1, 0])
    #~ tb.add_hopping(t1, (0, 1), (1, 1), [0, -1, 0])
    #~ tb.add_hopping(t1, (0, 0), (1, 0), [0, 0, 0])
    #~ tb.add_hopping(t1, (0, 0), (1, 0), [-1, 0, 0])
    #~ tb.add_hopping(t1, (0, 0), (1, 0), [-1, -1, 0])
    #~ tb.add_hopping(t1, (0, 0), (1, 0), [0, -1, 0])
    
    tb.add_hopping(t2, (0, 0), (0, 0), [1, 0, 0])
    tb.add_hopping(t2, (0, 0), (0, 0), [0, 1, 0])
    tb.add_hopping(t2, (0, 0), (0, 0), [-1, 0, 0])
    tb.add_hopping(t2, (0, 0), (0, 0), [0, -1, 0])
    tb.add_hopping(t2, (0, 1), (0, 1), [1, 0, 0])
    tb.add_hopping(t2, (0, 1), (0, 1), [0, 1, 0])
    tb.add_hopping(t2, (0, 1), (0, 1), [-1, 0, 0])
    tb.add_hopping(t2, (0, 1), (0, 1), [0, -1, 0])
    tb.add_hopping(-t2, (1, 1), (1, 1), [1, 0, 0])
    tb.add_hopping(-t2, (1, 1), (1, 1), [0, 1, 0])
    tb.add_hopping(-t2, (1, 1), (1, 1), [-1, 0, 0])
    tb.add_hopping(-t2, (1, 1), (1, 1), [0, -1, 0])
    tb.add_hopping(-t2, (1, 0), (1, 0), [1, 0, 0])
    tb.add_hopping(-t2, (1, 0), (1, 0), [0, 1, 0])
    tb.add_hopping(-t2, (1, 0), (1, 0), [-1, 0, 0])
    tb.add_hopping(-t2, (1, 0), (1, 0), [0, -1, 0])
    tb.create_hamiltonian()
    tb_system = z2pack.TightBinding(tb)
    tb_plane = tb_system.plane(1, 2, 0, pickle_file = 'pickle_tb.txt', Nstrings=40)
    tb_plane.wcc_calc(verbose = True)
    tb_plane.plot()
    print("invariant: " + str(tb_plane.invariant()))
    """
    """
