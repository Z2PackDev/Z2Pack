#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    squarelattice.py

import sys
sys.path.append("../../")
import z2pack.tb as tb

import os
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

def calculate_system(ax, t1, t2, **kwargs):

    H = tb.Hamilton()

    # create the two atoms
    H.add_atom(([1, 1], 1), [0, 0, 0])
    H.add_atom(([-1, -1], 1), [0.5, 0.5, 0])

    # add hopping between different atoms
    H.add_hopping(((0, 0), (1, 1)), tb.vectors.combine([0,-1],[0,-1],0), t1, phase = [1, -1j, 1j, -1])
    H.add_hopping(((0, 1), (1, 0)), tb.vectors.combine([0,-1],[0,-1],0), t1, phase = [1, 1j, -1j, -1])

    # add hopping between neighbouring orbitals of the same type
    H.add_hopping((((0, 0), (0, 0)),((0, 1), (0, 1))), tb.vectors.neighbours([0,1]), t2)
    H.add_hopping((((1, 1), (1, 1)),((1, 0), (1, 0))), tb.vectors.neighbours([0,1]), -t2)

    # call to Z2Pack
    tb_system = tb.System(H)
    tb_surface = tb_system.surface(lambda kx: [kx / 2., 0, 0], [0, 1, 0], pickle_file = './results/res.txt')
    tb_surface.wcc_calc(**kwargs)

    plot = tb_surface.plot(show = False, axis = ax)

    
    print("t1: {0}, t2: {1}, invariant: {2}".format(t1, t2, tb_surface.invariant()))
    return plot, tb_surface
        
if __name__ == "__main__":
    if not os.path.exists('./results'):
        os.makedirs('./results')

    settings = {'num_strings': 5, 'verbose': True}
    t_values = [[0.2, 0.3], [0.1, 0.4], [-0.2, -0.3], [0.0, 0.3]]

    fig, axes = plt.subplots(2,2)
    for i, ax in enumerate(axes.flatten()):
        calculate_system(ax, *t_values[i], **settings)

    plt.savefig('./results/squarelattice.pdf', bbox_inches = 'tight')
