#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    27.09.2014 15:39:41 CEST
# File:    HgTe_plot.py

import sys
sys.path.append('../../../')
import z2pack
import matplotlib.pyplot as plt

import os

"""
HgTesmuth example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

def k_points(start_point, last_point, end_point, N):
    string = '\nkptopt -1\nndivk ' + str(N - 1) + '\nkptbounds '
    for coord in start_point:
        string += str(coord).replace('e','d') + ' '
    string += '\n'
    for coord in last_point:
        string += str(coord).replace('e','d') + ' '
    string += '\n'
    return string
    
    
# creating the z2pack.abinit object
HgTe = z2pack.fp.System(    ['HgTe_nscf.files', 'HgTe_nscf.in', 'wannier90.win' ],
                                k_points,
                                'HgTe_nscf.in',
                                'build',
                                'mpirun -np 7 abinit < HgTe_nscf.files >& log'
                    )
    

# creating the z2pack.plane object
plane_0 = HgTe.plane(2, 0, 0, pickle_file = './results/res_0.txt')
plane_1 = HgTe.plane(2, 0, 0.5, pickle_file = './results/res_1.txt')

fig, ax = plt.subplots()
plane_0.load()
plane_0.plot(show=False, axis=ax)
ax.set_title(r'Plane $k_1 = {}$, Invariant $\Delta = {}$'.format(0, plane_0.invariant()))
ax.set_xlabel(r'$k_3$')
ax.set_ylabel(r'$x_2$')
plt.savefig('./results/HgTe_1.pdf', bbox_inches = 'tight')

ax.cla()
plane_1.load()
plane_1.plot(show=False, axis=ax)
ax.set_title(r'Plane $k_1 = {}$, Invariant $\Delta = {}$'.format(0.5, plane_1.invariant()))
ax.set_xlabel(r'$k_3$')
ax.set_ylabel(r'$x_2$')
plt.savefig('./results/HgTe_2.pdf', bbox_inches = 'tight')

