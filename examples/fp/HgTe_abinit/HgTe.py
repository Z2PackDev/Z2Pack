#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    HgTe.py

import sys
sys.path.append("../../../")
import z2pack

import os

"""
HgTe example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

# creating the z2pack.abinit object
HgTe = z2pack.fp.System(["HgTe_nscf.files", "HgTe_nscf.in", "wannier90.win" ],
                        z2pack.fp.kpts.abinit,
                        "HgTe_nscf.in",
                        "build",
                        "mpirun -np 7 abinit < HgTe_nscf.files >& log",
                        executable='/bin/bash'
                    )
    

# creating the z2pack.plane object
plane_0 = HgTe.plane(2, 0, 0, pickle_file = 'results/res_0.txt')
plane_1 = HgTe.plane(2, 0, 0.5, pickle_file = 'results/res_1.txt')

# WCC calculation
plane_0.wcc_calc(no_iter=True)
plane_1.wcc_calc(no_iter=True)
    

