#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

import z2pack

# Edit the paths to your Quantum Espresso 6+ and Wannier90 2.1+ here
QEDIR = '/home/greschd/software/qe-6.0/bin/'
WANDIR = '/home/greschd/software/wannier90-2.1.0'

# Commands to run pw, pw2wannier90, wannier90
MPIRUN = 'mpirun -np 4 '
PWCMD = MPIRUN + os.path.join(QEDIR, 'pw.x ')
PW2WANCMD = MPIRUN + os.path.join(QEDIR, 'pw2wannier90.x ')
WANCMD = os.path.join(WANDIR, 'wannier90.x')

Z2CMD = (WANCMD + ' MoP2 -pp;' +
         PWCMD + '< MoP2.nscf.in >& pw.log;' +
         PW2WANCMD + '< MoP2.pw2wan.in >& pw2wan.log;')

# creating the results folder, running the SCF calculation if needed
os.makedirs('./plots', exist_ok=True)
os.makedirs('./results', exist_ok=True)
if not os.path.exists('./scf'):
    os.makedirs('./scf')
    print("Running the scf calculation")
    shutil.copyfile('input/MoP2.scf.in', 'scf/MoP2.scf.in')
    out = subprocess.call(PWCMD + ' < MoP2.scf.in > scf.out', shell=True, cwd='./scf')
    if out != 0:
        raise RuntimeError('Error in SCF call. Inspect scf folder for details, and delete it to re-run the SCF calculation.')

# Copying the lattice parameters from MoP2.save/data-file.xml into MoP2.win
cell = ET.parse('scf/MoP2.save/data-file.xml').find('CELL').find('DIRECT_LATTICE_VECTORS')
unit = cell[0].attrib['UNITS']
lattice = '\n '.join([line.text.strip('\n ') for line in cell[1:]])

with open('input/tpl_MoP2.win', 'r') as f:
    tpl_MoP2_win = f.read()
with open('input/MoP2.win', 'w') as f:
    f.write(tpl_MoP2_win.format(unit=unit, lattice=lattice))

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
input_files = ['input/' + name for name in ["MoP2.nscf.in", "MoP2.pw2wan.in", "MoP2.win" ]]
system = z2pack.fp.System(
    input_files=input_files,
    kpt_fct=[z2pack.fp.kpoint.qe_explicit, z2pack.fp.kpoint.wannier90_full],
    kpt_path=["MoP2.nscf.in", "MoP2.win"],
    command=Z2CMD,
    executable='/bin/bash',
    mmn_path='MoP2.mmn'
)

# Run the WCC calculations
# a small sphere around one Weyl point
result_1 = z2pack.surface.run(
    system=system,
    surface=z2pack.shape.Sphere(center=(0.6239797, 0.70845137, 0), radius=0.007),
    save_file='./results/res1.json',
    load=True
)
# a small sphere around the other Weyl point
result_2 = z2pack.surface.run(
    system=system,
    surface=z2pack.shape.Sphere(center=(0.61197818, 0.70080602, 0), radius=0.007),
    save_file='./results/res2.json',
    load=True
)
# a bigger sphere around both Weyl points
result_3 = z2pack.surface.run(
    system=system,
    surface=z2pack.shape.Sphere(center=(0.61797894, 0.7046287, 0.), radius=0.014),
    save_file='./results/res3.json',
    load=True
)

# Combining the two plots
fig, ax = plt.subplots(3, 1, sharex=True, figsize=(5, 12))
for res, axis in zip([result_1, result_2, result_3], ax):
    z2pack.plot.chern(res, axis=axis)
plt.savefig('plots/plot.pdf', bbox_inches='tight')

print('Chern number / Weyl chirality around WP1: {0}'.format(z2pack.invariant.chern(result)))
print('Chern number / Weyl chirality around WP2: {0}'.format(z2pack.invariant.chern(result)))
print('Chern number / Weyl chirality around both Weyl points: {0}'.format(z2pack.invariant.chern(result)))
