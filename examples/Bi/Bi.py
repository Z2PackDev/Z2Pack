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

def k_points(start_point, last_point, end_point, N):
    string = "\nkptopt -1\nndivk " + str(N - 1) + '\nkptbounds '
    for coord in start_point:
        string += str(coord).replace('e','d') + ' '
    string += '\n'
    for coord in last_point:
        string += str(coord).replace('e','d') + ' '
    string += '\n'
    return string
    
    
# creating the z2pack.abinit object
Bi = z2pack.FirstPrinciples(    ["Bi_nscf.files", "Bi_nscf.in", "wannier90.win" ],
                                k_points,
                                "Bi_nscf.in",
                                "build",
                                "mpirun -np 7 abinit < Bi_nscf.files >& log"
                    )
    

# creating the z2pack.plane object
Bi_plane = Bi.plane(2, 0, 0, pickle_file = 'Bi_01_pickle.txt')

# WCC calculation
Bi_plane.wcc_calc(no_iter = True, no_neighbour_check = True)
    

