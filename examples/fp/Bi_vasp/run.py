#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    07.02.2015 04:21:23 CET
# File:    run.py

import os
import z2pack
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
# The command (mpirun ...) will have to be replaced to match your system.
system = z2pack.fp.System(["input/CHGCAR", "input/INCAR", "input/POSCAR", "input/POTCAR", "input/wannier90.win" ],
                          z2pack.fp.kpts.vasp,
                          "KPOINTS",
                          "mpirun $VASP >& log" 
                    )

if not os.path.exists('./results'):
    os.mkdir('./results')
    

# Creating two surfaces, both with the pumping parameter t changing
# ky from 0 to 0.5, and strings along kz.
# The first plane is at kx = 0, the second one at kx = 0.5
# Notice the different values of pickle_file to avoid overwriting the data.
surface_0 = system.surface(lambda t: [0, t / 2, 0], [0, 0, 1],
                           pickle_file = './results/res_0.txt')
surface_1 = system.surface(lambda t: [0.5, t / 2, 0], [0, 0, 1],
                           pickle_file = './results/res_1.txt')

# WCC calculation - standard settings
surface_0.load(quiet=True)
surface_0.wcc_calc()    
surface_1.load(quiet=True)
surface_1.wcc_calc()

# Combining the two plots
fig, ax = plt.subplots(1, 2, sharey=True, figsize = (9,5))
surface_0.wcc_plot(show=False, axis=ax[0])
surface_1.wcc_plot(show=False, axis=ax[1])
plt.savefig('plots/plot.pdf', bbox_inches = 'tight')

print('Z2 topological invariant at kx = 0: {0}'.format(surface_0.invariant()))
print('Z2 topological invariant at kx = 0.5: {0}'.format(surface_1.invariant()))
