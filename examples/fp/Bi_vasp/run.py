#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    07.02.2015 04:21:23 CET
# File:    run.py

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import z2pack

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
# The command (mpirun ...) will have to be replaced to match your system.
system = z2pack.fp.System(
    input_files=["input/CHGCAR", "input/INCAR", "input/POSCAR", "input/POTCAR", "input/wannier90.win" ],
    kpt_fct=z2pack.fp.kpoint.vasp,
    kpt_path="KPOINTS",
    command="mpirun $VASP >& log" 
)

if not os.path.exists('./results'):
    os.mkdir('./results')
if not os.path.exists('./plots'):
    os.mkdir('./plots')
    

# Running the WCC calculation - standard settings
result_0 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0, s / 2, t],
    save_file = './results/res_0.p',
    load=True
)
result_1 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0.5, s / 2, t],
    save_file = './results/res_1.p',
    load=True
)

# Plotting WCC evolution
fig, ax = plt.subplots(1, 2, sharey=True, figsize = (9,5))

z2pack.plot.wcc(result_0, axis=ax[0])
z2pack.plot.wcc(result_1, axis=ax[1])
plt.savefig('plots/plot.pdf', bbox_inches = 'tight')

print('Z2 topological invariant at kx = 0: {0}'.format(z2pack.surface.invariant.z2(result_0)))
print('Z2 topological invariant at kx = 0.5: {0}'.format(z2pack.surface.invariant.z2(result_1)))
