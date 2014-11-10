#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    BiSe.py

import sys
sys.path.append("../../../")
import z2pack

import os

"""
Bismuth Selenide example
"""

if __name__ == "__main__":

    if not os.path.exists('./results'):
        os.makedirs('./results')

    # creating the z2pack.abinit object
    BiSe = z2pack.fp.System(["BiSe_nscf.files", "BiSe_nscf.in", "wannier90.win" ],
                            z2pack.fp.kpts.abinit,
                            "BiSe_nscf.in",
                            "build",
                            "mpirun -np 6 abinit < BiSe_nscf.files >& log",
                            executable='/bin/bash'
                            )

    # plane at k1=0
    plane_0 = BiSe.plane(2, 0, 0, pickle_file = 'results/res_0.txt')
    #~ plane_0.wcc_calc(no_iter=True, no_neighbour_check=False)

    # plane at k1=Pi
    plane_1 = BiSe.plane(2, 0, 0.5, pickle_file = 'results/res_1.txt')
    plane_1.wcc_calc(no_iter=True, no_neighbour_check=False)
