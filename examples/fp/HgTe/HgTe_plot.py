#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    27.09.2014 15:39:41 CEST
# File:    HgTe_plot.py

import sys
sys.path.append("../../../")
import z2pack
import matplotlib.pyplot as plt

import os

"""
HgTesmuth example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

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
HgTe = z2pack.fp.System(    ["HgTe_nscf.files", "HgTe_nscf.in", "wannier90.win" ],
                                k_points,
                                "HgTe_nscf.in",
                                "build",
                                "mpirun -np 7 abinit < HgTe_nscf.files >& log"
                    )
    

# creating the z2pack.plane object
HgTe_plane = HgTe.plane(2, 0, 0, pickle_file = './results/res.txt')

# WCC calculation
"""
no need to re-do the calculation
"""
#~ HgTe_plane.wcc_calc(no_iter = True, no_neighbour_check = True)

HgTe_plane.load()
fig, ax = plt.subplots(1, figsize = (9,5))
HgTe_plane.plot(show = False, axis = ax)
plt.savefig('./results/HgTe.pdf', bbox_inches = 'tight')

print('Z2 topological invariant: {0}'.format(HgTe_plane.invariant()))
    

