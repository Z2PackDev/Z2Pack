#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    27.09.2014 15:39:41 CEST
# File:    BiSe_plot.py

import sys
sys.path.append("../../../")
import z2pack
import matplotlib.pyplot as plt

import os

"""
Bismuth Selenide example
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
BiSe = z2pack.fp.System(["BiSe_nscf.files", "BiSe_nscf.in", "wannier90.win" ],
                        k_points,
                        "BiSe_nscf.in",
                        "build",
                        "mpirun -np 7 abinit < BiSe_nscf.files >& log")


# creating the z2pack.plane object
BiSe_plane = BiSe.plane(2, 0, 0, pickle_file = './results/res.txt')

# WCC calculation
"""
no need to re-do the calculation
"""
#~ BiSe_plane.wcc_calc(no_iter = True, no_neighbour_check = True)

BiSe_plane.load()
fig, ax = plt.subplots(1, figsize = (9,5))
BiSe_plane.plot(show = False, ax = ax)
plt.savefig('./results/BiSe.pdf', bbox_inches = 'tight')

print('Z2 topological invariant: {0}'.format(BiSe_plane.invariant()))


