#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    Bi.py

import sys
sys.path.append("../../src/")
import z2pack

"""
Bismuth example
"""

# creating the z2pack.abinit object
Bi = z2pack.Abinit( "Bi", 
                    "Bi_common.in", 
                    "../Psps/83bi.5.hgh", 
                    "./build", 
                    10, 
                    abinit_command = "mpirun -np 7 abinit")
    
    
# SCF run - comment if necessary (SCF needs to be run only once)
#~ Bi.scf("Bi_scf.in", clean_subfolder = True)

# creating the z2pack.plane object
Bi_plane = Bi.plane(2, 0, 0, pickle_file = 'build/Bi_01_pickle.txt')

# WCC calculation
Bi_plane.wcc_calc()
    

