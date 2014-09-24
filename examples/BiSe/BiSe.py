#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    BiSe.py

import sys
sys.path.append("../../src/")
import z2pack

"""
Bismuth Selenide example
"""

# creating the z2pack.abinit object
BiSe = z2pack.Abinit(   "BiSe", 
                        "BiSe_common.in", 
                        ["../Psps/83bi.5.hgh","../Psps/34se.6.hgh"], 
                        "./build", 
                        10, 
                        abinit_command = "mpirun -np 7 abinit")
    
    
# SCF run - comment if necessary (SCF needs to be run only once)
#~ BiSe.scf("BiSe_scf.in", setup_only = True)

# creating the z2pack.plane object
BiSe_1 = BiSe.plane(2, 0, 0, pickle_file = 'build/BiSe_01_pickle.txt')
BiSe_2 = BiSe.plane(2, 0, 0.5, pickle_file = 'build/BiSe_02_pickle.txt')

# WCC calculation
BiSe_1.wcc_calc()
BiSe_2.wcc_calc()
    
# plots and evaluation
BiSe_1.plot()
print("The Z2 topological invariant for this plane is " + str(BiSe_1.invariant()))
BiSe_2.plot()
print("The Z2 topological invariant for this plane is " + str(BiSe_2.invariant()))    
    
