#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Gabriel Autes, Dominik Gresch <greschd@gmx.ch>
# Date:    26.04.2015 20:26:10 CEST
# File:    run.py

import z2pack

import os
import shutil
import subprocess
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

# Edit the paths to your Quantum Espresso and Wannier90 here
qedir = '/home/greschd/software/espresso-5.1.2/bin/'
wandir = '/home/greschd/software/wannier90-1.2'

# Commands to run pw, pw2wannier90, wannier90
mpirun = 'mpirun -np 4 '
pwcmd = mpirun + qedir + '/pw.x '
pw2wancmd = mpirun + qedir + '/pw2wannier90.x '
wancmd = wandir + '/wannier90.x'

z2cmd = (wancmd + ' bi -pp;' +
         pwcmd + '< bi.nscf.in >& pw.log;' +
         pw2wancmd + '< bi.pw2wan.in >& pw2wan.log;')

# creating the results folder, running the SCF calculation if needed
if not os.path.exists('./plots'):
    os.mkdir('./plots')
if not os.path.exists('./results'):
    os.mkdir('./results')
if not os.path.exists('./scf'):
    os.makedirs('./scf')
    print("Running the scf calculation")
    shutil.copyfile('input/bi.scf.in', 'scf/bi.scf.in')
    subprocess.call(pwcmd + ' < bi.scf.in > scf.out', shell=True, cwd='./scf')

# Copying the lattice parameters from bi.save/data-file.xml into bi.win
cell = ET.parse('scf/bi.save/data-file.xml').find('CELL').find('DIRECT_LATTICE_VECTORS')
unit = cell[0].attrib['UNITS']
lattice = '\n '.join([line.text.strip('\n ') for line in cell[1:]])

with open('input/tpl_bi.win', 'r') as f:
    tpl_bi_win = f.read()
with open('input/bi.win', 'w') as f:
    f.write(tpl_bi_win.format(unit=unit, lattice=lattice))

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
input_files = ['input/' + name for name in ["bi.nscf.in", "bi.pw2wan.in", "bi.win" ]]
system = z2pack.fp.System(input_files,
                          [z2pack.fp.kpts.qe, z2pack.fp.kpts.wannier90],
                          ["bi.nscf.in","bi.win"],
                          z2cmd,
                          executable='/bin/bash',
                          mmn_path='bi.mmn')

# Run the WCC calculations
result_0 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0, s / 2, t], 
    save_file='./results/res_0.p',
    load=True
)
result_1 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0.5, s / 2, t],
    save_file='./results/res_1.p',
    load=True
)

# Combining the two plots
fig, ax = plt.subplots(1, 2, sharey=True, figsize=(9,5))
z2pack.surface.plot.wcc(result_0, ax=ax[0])
z2pack.surface.plot.wcc(result_1, ax=ax[1])
plt.savefig('plots/plot.pdf', bbox_inches='tight')

print('Z2 topological invariant at kx = 0: {0}'.format(z2pack.surface.invariant.z2(result_0)))
print('Z2 topological invariant at kx = 0.5: {0}'.format(z2pack.surface.invariant.z2(result_1)))
