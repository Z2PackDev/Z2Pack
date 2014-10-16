#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    Bi.py

import sys
sys.path.append("../../../src/")
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
                        "mpirun -np 7 abinit < Bi_nscf.files >& log"
                    )
    

# creating the z2pack.plane object
Bi_plane = Bi.plane(2, 0, 0, pickle_file = 'results/res.txt')

# WCC calculation
Bi_plane.wcc_calc(no_iter = True, no_neighbour_check = True)
    

