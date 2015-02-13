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
    BiSe2 = z2pack.fp.System(["BiSe2_nscf.files", "BiSe2_nscf.in", "wannier90.win" ],
                            z2pack.fp.kpts.abinit,
                            "BiSe2_nscf.in",
                            "mpirun -np 6 abinit < BiSe2_nscf.files >& log",
                            executable='/bin/bash'
                            )

    # surface at k1=0
    surface_0 = BiSe2.surface(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = 'results/BiSe2_0.txt')
    surface_0.wcc_calc()

    # surface at k1=Pi
    surface_1 = BiSe2.surface(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = 'results/BiSe2_1.txt')
    surface_1.wcc_calc()
