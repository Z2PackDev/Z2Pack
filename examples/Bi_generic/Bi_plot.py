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
Bi = z2pack.Abinit( "Bi", "Bi_common.in", "../Psps/83bi.5.hgh", './build', 10, abinit_command = "mpirun -np 7 abinit")
    
    
# SCF run - comment if necessary (SCF needs to be run only once)
"""
we don't need to do the calculations again
"""
#~ Bi.scf("Bi_scf.in")

# creating the z2pack.plane object
Bi_plane = Bi.plane(2, 0, 0, pickle_file = 'build/Bi_01_pickle.txt')

# WCC calculation
"""
we don't need to do the calculations again
"""
#~ Bi_plane.wcc_calc()
    
Bi_plane.load()
Bi_plane.plot()
print("The Z2 topological invariant for this plane is " + str(Bi_plane.invariant()))

