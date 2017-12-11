#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

import scipy.linalg as la
import numpy as np
import z2pack

# Edit the paths to your Quantum Espresso and Wannier90 here
qedir = '/home/tony/qe-6.2/bin'
wandir = '/home/tony/wannier90-2.1.0'

# Commands to run pw, pw2wannier90, wannier90
mpirun = ''
pwcmd = 'pw.x '
pw2wancmd = mpirun + qedir + '/pw2wannier90.x '
wancmd = wandir + '/wannier90.x'

z2cmd = (
    wancmd + ' bi -pp;' + pwcmd + '< bi.nscf.in >& pw.log;' + pw2wancmd +
    '< bi.pw2wan.in >& pw2wan.log;'
)

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
cell = ET.parse('scf/bi.xml').find('output').find('atomic_structure'
                                                  ).find('cell')
unit = cell.get('unit', 'Bohr')
lattice = '\n'.join([cell.find(vec).text for vec in ['a1', 'a2', 'a3']])

with open('input/tpl_bi.win', 'r') as f:
    tpl_bi_win = f.read()
with open('input/bi.win', 'w') as f:
    f.write(tpl_bi_win.format(unit=unit, lattice=lattice))

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
input_files = [
    'input/' + name for name in ["bi.nscf.in", "bi.pw2wan.in", "bi.win", "bi.sym"]
]
system = z2pack.fp.System(
    input_files=input_files,
    kpt_fct=[z2pack.fp.kpoint.qe, z2pack.fp.kpoint.wannier90_full],
    kpt_path=["bi.nscf.in", "bi.win"],
    command=z2cmd,
    executable='/bin/bash',
    mmn_path='bi.mmn',
    xml_path='bi.xml',
    dmn_path='bi.dmn'
)


symms = system.suggest_symmetry_surfaces()
s = symms[3] #select one of the suggested symmetries as an example.
print("Symmetry:")
print(s.symm)
print("Vectors spanning surface:")
print(s.vectors[1:])

# Run the WCC calculations
# The tolerances have to be turned of because this is not a physical system and the calculation does not converge
result = z2pack.surface.run(
    system=system,
    surface=s.surface_lambda,
    iterator=range(8, 11, 2),
    save_file='./results/res_0.json',
    load=True,
    use_symm=True,
    pos_tol=None,
    gap_tol=None,
    move_tol=None
)

print("Symmetries:")
print(result.symm_list)

#project to each eigenvalue of the symmetry for which we calculated the surface
ew = np.unique(la.eig(result.symm_list[1])[0])
fig, ax = plt.subplots(1, len(ew)+1, sharey=True, figsize=(12, 5))
z2pack.plot.wcc(result, axis=ax[0])
ax[0].set_title("Unprojected system")

print(
    'Z2 invariant of unprojected system: {}'.format(
        z2pack.invariant.z2(result)
    )
)

for i, w in enumerate(ew):
    result_projected = result.symm_project(w, isym=1)
    z2pack.plot.wcc(result_projected, axis=ax[i+1])
    ax[i+1].set_title("Projection on $Eig_{{{}}}(S)$".format(w))
    print(
        'Z2 invariant of projected system (eigenvalue: {}): {}'.format(
            round(w, 2),
            z2pack.invariant.z2(result_projected)
        )
    )

plt.savefig('plots/plot.pdf', bbox_inches='tight')


