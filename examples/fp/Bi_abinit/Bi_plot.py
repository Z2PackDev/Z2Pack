#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    27.09.2014 15:39:41 CEST
# File:    Bi_plot.py

import sys
sys.path.append("../../../")
import z2pack
import matplotlib.pyplot as plt

import os

"""
Bismuth example
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
Bi = z2pack.fp.System(    ["Bi_nscf.files", "Bi_nscf.in", "wannier90.win" ],
                                k_points,
                                "Bi_nscf.in",
                                "build",
                                "mpirun -np 7 abinit < Bi_nscf.files >& log"
                    )
    

# creating the z2pack.plane object
plane_0 = Bi.plane(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = './results/res_0.txt')
plane_0 = Bi.plane(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = './results/res_1.txt')

# WCC calculation
"""
no need to re-do the calculation
"""

plane_0.load()
plane_1.load()
fig, ax = plt.subplots(1, 2, sharey=True, figsize = (9,5))
plane_0.plot(show=False, axis=ax[0])
plane_1.plot(show=False, axis=ax[1])
plt.savefig('./results/Bi.pdf', bbox_inches = 'tight')

print('Z2 topological invariant: {0}'.format(plane_0.invariant()))
print('Z2 topological invariant: {0}'.format(plane_1.invariant()))
    

