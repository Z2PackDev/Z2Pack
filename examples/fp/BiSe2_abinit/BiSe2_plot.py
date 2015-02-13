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


# creating the z2pack.abinit object
BiSe = z2pack.fp.System(["BiSe_nscf.files", "BiSe_nscf.in", "wannier90.win" ],
                        z2pack.fp.kpts.abinit,
                        "BiSe_nscf.in",
                        "build",
                        "mpirun -np 7 abinit < BiSe_nscf.files >& log")


# creating the z2pack.plane object
plane_0 = BiSe.plane(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = './results/res_0.txt')
plane_1 = BiSe.plane(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = './results/res_1.txt')


plane_0.load()
plane_1.load()
fig, ax = plt.subplots(2, sharex=True, figsize = (9,5))
fig.subplots_adjust(hspace=0.4)
plane_0.plot(show = False, axis=ax[0], shift=0.5)
ax[0].set_title(r'$k_1 = 0,$ $\Delta = {}$'.format(plane_0.invariant()))
ax[0].set_ylabel(r'$x_3$')
ax[0].set_xlabel('')
plane_1.plot(show = False, axis=ax[1], shift=0.5)
ax[1].set_title(r'$k_1 = 0.5,$ $\Delta = {}$'.format(plane_1.invariant()))
ax[1].set_ylabel(r'$x_3$')
ax[1].set_xlabel(r'$k_2$')
plt.savefig('./results/BiSe.pdf', bbox_inches = 'tight')



