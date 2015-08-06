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
Bi = z2pack.fp.System(['Bi_nscf.files', 'Bi_nscf.in', 'wannier90.win' ],
                      z2pack.fp.kpts.abinit,
                      'Bi_nscf.in',
                      'mpirun ~/software/abinit-7.8.2/src/98_main/abinit < Bi_nscf.files >& log',
                      executable='/bin/bash'
                     )
    

# creating the Surface object
surface_0 = Bi.surface(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = './results/Bi_0.txt')
surface_1 = Bi.surface(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = './results/Bi_1.txt')

# WCC calculation
surface_0.wcc_calc()
surface_1.wcc_calc()
    

