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

# creating the z2pack.abinit object
Bi = z2pack.fp.System(   ["Bi_nscf.files", "Bi_nscf.in", "wannier90.win" ],
                        z2pack.fp.kpts.abinit,
                        "Bi_nscf.in",
                        "build",
                        "mpirun ~/software/abinit-7.8.2/src/98_main/abinit < Bi_nscf.files >& log"
                    )
    

# creating the z2pack.plane object
plane_0 = Bi.plane(2, 0, 0, pickle_file = 'results/res_0.txt')
plane_1 = Bi.plane(2, 0, 0.5, pickle_file = 'results/res_1.txt')

# WCC calculation
plane_0.wcc_calc()
plane_1.wcc_calc()
    

