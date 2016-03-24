#!/usr/bin/env python
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
Bi = z2pack.fp.System(['input/Bi_nscf.files', 'input/Bi_nscf.in', 'input/wannier90.win' ],
                      z2pack.fp.kpts.abinit,
                      'Bi_nscf.in',
                      'mpirun -np 4 ~/software/abinit-7.8.2/src/98_main/abinit < Bi_nscf.files >& log',
                      executable='/bin/bash'
                     )
    

# creating the Surface object
result_0 = z2pack.surface.run(system=Bi, surface=lambda s, t: [0, s / 2, t], save_file = './results/Bi_0.p', load=True)
result_0 = z2pack.surface.run(system=Bi, surface=lambda s, t: [0.5, s / 2, t], save_file = './results/Bi_1.p', load=True)

# WCC calculation
print(z2pack.surface.invariant.wcc(result_0))
print(z2pack.surface.invariant.wcc(result_1))
