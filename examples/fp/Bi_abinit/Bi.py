#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    Bi.py

import sys
sys.path.append("../../../")
import z2pack

import os

"""
Bismuth example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

# creating the Z2PackSystem object
# the command (mpirun ...) will have to be replaced
Bi = z2pack.fp.System(["Bi_nscf.files", "Bi_nscf.in", "wannier90.win" ],
                      z2pack.fp.kpts.abinit,
                      "Bi_nscf.in",
                      "build",
                      "mpirun ~/software/abinit-7.8.2/src/98_main/abinit < Bi_nscf.files >& log"
                    )
    

# creating the Z2PackPlane object
plane_0 = Bi.plane(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = './results/res_0.txt')
plane_0 = Bi.plane(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = './results/res_1.txt')

# WCC calculation
plane_0.wcc_calc()
plane_1.wcc_calc()
    

