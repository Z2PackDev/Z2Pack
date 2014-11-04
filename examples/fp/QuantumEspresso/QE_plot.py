#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    QE_plot.py

import sys
sys.path.append("../../../")
import z2pack

import os

"""
Quantum Espresso example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

# creating the System
system = z2pack.fp.System(
    ["input_file_1", "input_file_2", "wannier90.win" ],
    z2pack.fp.kpts.quantum_espresso, # TO BE IMPLEMENTED
    "Input file where the k-point string goes",
    "build",
    "Command for calling Quantum Espresso"
)
    

# creating the plane
plane = Bi.plane(2, 0, 0, pickle_file = 'results/res.txt')

# reloading from pickle file
plane.load()
fig, ax = plt.subplots(1, figsize = (9,5))
plane.plot(show = False, ax = ax)
plt.savefig('./results/QE.pdf', bbox_inches = 'tight')

print('Z2 topological invariant: {0}'.format(plane.invariant()))
    

