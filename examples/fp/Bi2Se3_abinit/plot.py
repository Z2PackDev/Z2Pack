#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    27.09.2014 15:39:41 CEST
# File:    Bi2Se3_plot.py

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
Bi2Se3 = z2pack.fp.System(["Bi2Se3_nscf.files", "Bi2Se3_nscf.in", "wannier90.win" ],
                        z2pack.fp.kpoint.abinit,
                        "Bi2Se3_nscf.in",
                        "build",
                        "mpirun -np 7 abinit < Bi2Se3_nscf.files >& log")


# creating the z2pack.surface object
surface_0 = Bi2Se3.surface(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = './results/res_0.txt')
surface_1 = Bi2Se3.surface(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = './results/res_1.txt')


surface_0.load()
surface_1.load()
fig, ax = plt.subplots(2, sharex=True, figsize = (9,5))
fig.subplots_adjust(hspace=0.4)
surface_0.plot(show = False, axis=ax[0], shift=0.5)
ax[0].set_title(r'$k_1 = 0,$ $\Delta = {}$'.format(surface_0.invariant()))
ax[0].set_ylabel(r'$x_3$')
ax[0].set_xlabel('')
surface_1.plot(show = False, axis=ax[1], shift=0.5)
ax[1].set_title(r'$k_1 = 0.5,$ $\Delta = {}$'.format(surface_1.invariant()))
ax[1].set_ylabel(r'$x_3$')
ax[1].set_xlabel(r'$k_2$')
plt.savefig('./results/Bi2Se3.pdf', bbox_inches = 'tight')
