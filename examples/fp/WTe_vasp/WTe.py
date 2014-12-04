#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    WTe.py

import sys
sys.path.append("../../../")
import z2pack

import os

"""
WTe example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

#~ # creating the z2pack.abinit object
#~ WTe = z2pack.fp.System(   ["INCAR", "CHGCAR"],
                        #~ z2pack.fp.kpts.vasp,
                        #~ "KPOINTS",
                        #~ "build",
                        #~ "mpirun -np 7 abinit < WTe_nscf.files >& log",
                        #~ executable='/bin/bash'
                    #~ )
    #~ 
#~ 
#~ # creating the z2pack.plane object
#~ plane_0 = WTe.plane(2, 0, 0, pickle_file = 'results/res_0.txt')
#~ plane_1 = WTe.plane(2, 0, 0.5, pickle_file = 'results/res_1.txt')
#~ 
#~ # WCC calculation
#~ plane_0.wcc_calc()
#~ plane_1.wcc_calc()

print(z2pack.fp.kpts.vasp([0, 0, 0],[0, 0, 0.9], [0, 0, 1], 10))
    

