#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    11.08.2016 00:03:52 CEST
# File:    run.py

import os

import z2pack
import matplotlib.pyplot as plt

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
# The command (mpirun ...) will have to be replaced to match your system.
SYSTEM_NAME = 'Bi2Se3'
system = z2pack.fp.System(
    input_files=[os.path.join('input', filename) for filename in [
        SYSTEM_NAME + '_nscf.files',
        SYSTEM_NAME + '_nscf.in',
        'wannier90.win'
    ]],
    kpt_fct=z2pack.fp.kpoint.abinit,
    kpt_path=SYSTEM_NAME + '_nscf.in',
    command='mpirun -np 7 ~/software/abinit-7.10.5/src/98_main/abinit < {}_nscf.files >& log'.format(SYSTEM_NAME),
    executable='/bin/bash'
)

# Surface calculation for surfaces at kx=0 and kx=0.5
# Standard settings are used
res_0 = z2pack.surface.run(
    system=system, 
    surface=lambda s, t: [0, s / 2, t],
    save_file='res_0.msgpack'
)
res_1 = z2pack.surface.run(
    system=system, 
    surface=lambda s, t: [0.5, s / 2, t],
    save_file='res_1.msgpack'
)

# Combining the two plots
fig, ax = plt.subplots(1, 2, sharey=True, figsize=(9, 5))
z2pack.plot.wcc(res_0, axis=ax[0])
z2pack.plot.wcc(res_1, axis=ax[1])
plt.savefig('plot.pdf', bbox_inches='tight')

print('Z2 topological invariant at kx = 0: {0}'.format(z2pack.invariant.z2(res_0)))
print('Z2 topological invariant at kx = 0.5: {0}'.format(z2pack.invariant.z2(res_1)))
