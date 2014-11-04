#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    QE.py

import sys
sys.path.append("../../../")
import z2pack

import os

"""
Quantum Espresso example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

# creating the System
system = z2pack.fp.System(
    ["input_file_1", "input_file_2", "wannier90.win" ],
    z2pack.fp.kpts.quantum_espresso, # Function generating k-points string
    "Input file where the k-point string goes",
    "build",
    "Command for calling Quantum Espresso"
)
    

# creating the plane
plane = Bi.plane(2, 0, 0, pickle_file = 'results/res.txt')

# WCC calculation
plane.wcc_calc(no_iter = True, no_neighbour_check = True)
    

