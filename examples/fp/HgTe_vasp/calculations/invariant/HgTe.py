#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    HgTe.py

import sys
sys.path.append("../../../../../")
import z2pack

import os

"""
WTe calculation
"""

if not os.path.exists('./results'):
    os.makedirs('./results')


string_dirs = [1, 1, 1, 1, 2, 2]
plane_pos_dirs = [2, 2, 0, 0, 1, 1]
plane_pos = [0, 0.5, 0, 0.5, 0, 0.5]

def calculate(i):
    WTe = z2pack.fp.System( ['INCAR', 'POSCAR', 'POTCAR', 'CHGCAR', 'wannier90.win'],
                            z2pack.fp.kpts.vasp,
                            "KPOINTS",
                            "build_" + str(i),
                            "mpirun $VASP_BIN/vasp.noncol >& log"
                        )
        
    plane = WTe.plane(string_dirs[i], plane_pos_dirs[i], plane_pos[i], pickle_file='results/res_fine_' + str(i) + '.txt')
    plane.wcc_calc(iterator=range(14, 62, 4), min_neighbour_dist=1e-3, num_strings=61)

if __name__ == "__main__":
    #~ for i in range(6):
    calculate(int(sys.argv[1]))
    print("HgTe.py")
