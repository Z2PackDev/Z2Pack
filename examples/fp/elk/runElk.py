# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import numpy as np
import z2pack2 as z2pack

# Edit the paths to your Elk and Wannier90 here
elkdir = '$HOME/Z2pack/elk-6.8.4/src/elk'


# creating the results folder, running the SCF calculation if needed
if not os.path.exists('./plots'):
    os.mkdir('./plots')
if not os.path.exists('./results'):
    os.mkdir('./results')
if not os.path.exists('./ground'):
    os.makedirs('./ground')
    print("Running the ground state calculation")    
    #copy all scf calc *.OUT files to wannBands folder, generate initial wannier90 files (*.win, *.mmn, etc.) 
    shutil.copyfile('input/elk.in', 'ground/elk.in')
    subprocess.call(elkdir + ' >& elkWannier.log', shell=True, cwd='./ground')

#%%Initial SCF calculation has run in the *.input directory


# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file. I am not entirely sure which files are absolutely necessary so this is an exhaustive list.
input_files = [    'ground/' + name for name in ["elk.in","STATE.OUT", "INFO.OUT", "GEOMETRY.OUT", "LINENGY.OUT", "DTOTENERGY.OUT", "EFERMI.OUT","EIGVAL.OUT", "EQATOMS.OUT", "EVALCORE.OUT", "EVALFV.OUT", "EVALSV.OUT","EVECFV.OUT","EVECSV.OUT", "FERMIDOS.OUT", "GAP.OUT", "GEOMETRY.OUT", "IADIST.OUT", "LATTICE.OUT","KPOINTS.OUT", "MOMENT.OUT", "MOMENTM.OUT","OCCSV.OUT","RMSDVS.OUT","SYMCRYS.OUT", "SYMLAT.OUT", "SYMSITE.OUT","TOTENERGY.OUT"]]

#note that this ensures that elkWannBands.in is used rather than what was used for the Ground state calculation. These all end up showing up in the Build directory
shutil.copyfile('input/elkWannBands.in', 'ground/elk.in')
system = z2pack.fp.System(
    input_files=input_files,
    kpt_fct=z2pack.fp.kpoint.elk,
    kpt_path="elk.in",
    command=elkdir+' >& elk.log',
    mmn_path='wannier.mmn'
)

# Run the WCC calculations
result_0 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0, s / 2, t],
    save_file='./results/res_0.json',
    load=True
)

print(
    'Z2 topological invariant at kx = 0: {0}'.format(
        z2pack.invariant.z2(result_0)
    )
)

# Plot the WCC
fig, ax = plt.subplots(1, 1, sharey=True, figsize=(9, 5))
z2pack.plot.wcc(result_0, axis=ax)
plt.savefig('plots/plot.pdf', bbox_inches='tight')


