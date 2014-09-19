#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    Bi.py

import sys
sys.path.append("../../../src/")
import z2pack

#-----------------------------------------------------------------------#
#                           BISMUTH EXAMPLE                             #
#-----------------------------------------------------------------------#

def calculate():
    Bi = z2pack.abinit( "Bi", "../Bi_common.in", "../../Psps/83bi.5.hgh", './', abinit_command = "mpirun -np 7 abinit", num_occupied = 10)

#----------------initial calculation - SCF------------------------------#
    Bi.scf("../Bi_scf.in")

#----------------WCC calculation----------------------------------------#
    Bi_1 = Bi.plane(2, 0, 0, pickle_file = 'Bi_01_pickle.txt')
    Bi_1.wcc_calc()
    
def plot():
    Bi = z2pack.abinit( "Bi", "../Bi_common.in", "../../Psps/83bi.5.hgh", './', abinit_command = "mpirun -np 7 abinit", num_occupied = 10)
    Bi_1 = Bi.plane(2, 0, 0, pickle_file = 'Bi_01_pickle.txt')
    Bi_1.load()
    Bi_1.plot()
    print("The Z2 topological invariant for this plane is" + str(Bi.invariant()))

if __name__ == "__main__":
    calculate()
    plot()
