#!/usr/bin/env python3
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
mpirun = 'mpirun -np 7 '
pwcmd = mpirun + qedir + '/pw.x '
pw2wancmd = mpirun + qedir + '/pw2wannier90.x '
wancmd = wandir + '/wannier90.x'

material_name = 'bi2se3'
z2cmd = (wancmd + ' ' + material_name + ' -pp;' +
         pwcmd + '< ' + material_name + '.nscf.in >& pw.log;' +
         pw2wancmd + '< ' + material_name + '.pw2wan.in >& pw2wan.log;')

# creating the results folder, running the SCF calculation if needed
if not os.path.exists('./plots'):
    os.mkdir('./plots')
if not os.path.exists('./results'):
    os.mkdir('./results')
if not os.path.exists('./scf'):
    os.mkdir('./scf')
    print("Running the scf calculation")
    shutil.copyfile('input/' + material_name + '.scf.in', 'scf/' + material_name + '.scf.in')
    subprocess.call(pwcmd+ " < " + material_name + ".scf.in > scf.out", shell=True, cwd='./scf')

# Copying the lattice parameters from bi.save/data-file.xml into bi.win
cell = ET.parse('scf/' + material_name + '.save/data-file.xml').find('CELL').find('DIRECT_LATTICE_VECTORS')
unit = cell[0].attrib['UNITS']
lattice = '\n '.join([line.text.strip('\n ') for line in cell[1:]])

with open('input/tpl_' + material_name + '.win', 'r') as f:
    tpl_bi_win = f.read()
with open('input/' + material_name + '.win', 'w') as f:
    f.write(tpl_bi_win.format(unit=unit, lattice=lattice))

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
input_files = ['input/' + name for name in [material_name + ".nscf.in", material_name + ".pw2wan.in", material_name + ".win" ]]
system = z2pack.fp.System(input_files,
                          [z2pack.fp.kpts.qe, z2pack.fp.kpts.wannier90],
                          [material_name + ".nscf.in", material_name + ".win"],
                          z2cmd,
                          executable='/bin/bash',
                          mmn_path=material_name + '.mmn')

    

# Creating two surfaces, both with the pumping parameter t changing
# ky from 0 to 0.5, and strings along kz.
# The first plane is at kx = 0, the second one at kx = 0.5
# Notice the different values of pickle_file to avoid overwriting the data.
surface_0 = system.surface(lambda t: [0, t / 2., 0], [0, 0, 1],
                           pickle_file='./results/res_0.txt')
surface_1 = system.surface(lambda t: [0.5, t / 2., 0], [0, 0, 1],
                           pickle_file='./results/res_1.txt')

# WCC calculation - standard settings
surface_0.load(quiet=True)
surface_0.wcc_calc()  
surface_1.load(quiet=True)
surface_1.wcc_calc()

# Combining the two plots
fig, ax = plt.subplots(1, 2, sharey=True, figsize=(9,5))
surface_0.wcc_plot(show=False, axis=ax[0])
surface_1.wcc_plot(show=False, axis=ax[1])
plt.savefig('plots/plot.pdf', bbox_inches='tight')

print('Z2 topological invariant at kx = 0: {0}'.format(surface_0.z2()))
print('Z2 topological invariant at kx = 0.5: {0}'.format(surface_1.z2()))
