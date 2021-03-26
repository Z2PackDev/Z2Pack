# -*- coding: utf-8 -*-
'''
run.py can be used to interface ELK and Z2Pack. To use, change elkdir to your location of elk.
Wannier90 is run by Elk in library mode. Check http://elk.sourceforge.net/ for installation
instructions.
'''
import os
import shutil
import subprocess

import matplotlib.pyplot as plt
import z2pack

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
    #do initial ground-state calculation in the ground folder using elk.in in the input folder
    shutil.copyfile('input/elk.in', 'ground/elk.in')
    subprocess.call(elkdir + ' >& elkWannier.log', shell=True, cwd='./ground')



# Collecting the files for the surface calculation
# The k-point nearest neighbors list/kpoints string is appended to the .in file,
# starting on the last line, and there can be no extra lines in between the shell_list
# and the nnkpts lines. The nnkpts line should be added directly to the end of elkWannBands.in
# automatically by Z2pack during the surface calculation (becomes build/elk.in).
input_files = [
    'ground/' + name for name in [
        "elk.in", "STATE.OUT", "INFO.OUT", "GEOMETRY.OUT", "LINENGY.OUT",
        "DTOTENERGY.OUT", "EFERMI.OUT", "EIGVAL.OUT", "EQATOMS.OUT",
        "EVALCORE.OUT", "EVALFV.OUT", "EVALSV.OUT", "EVECFV.OUT", "EVECSV.OUT",
        "FERMIDOS.OUT", "GAP.OUT", "GEOMETRY.OUT", "IADIST.OUT", "LATTICE.OUT",
        "KPOINTS.OUT", "MOMENT.OUT", "MOMENTM.OUT", "OCCSV.OUT", "RMSDVS.OUT",
        "SYMCRYS.OUT", "SYMLAT.OUT", "SYMSITE.OUT", "TOTENERGY.OUT"
    ]
]

# Note that this ensures that elkWannBands.in is used
# rather than what was used for the Ground state calculation.
shutil.copyfile('input/elkWannBands.in', 'ground/elk.in')

# Create the Z2Pack system.
system = z2pack.fp.System(input_files=input_files,
                          kpt_fct=z2pack.fp.kpoint.elk,
                          kpt_path="elk.in",
                          command=elkdir + ' >& elk.log',
                          mmn_path='wannier.mmn')

# Run the WCC calculations
result_0 = z2pack.surface.run(system=system,
                              surface=lambda s, t: [0, s / 2, t],
                              save_file='./results/res_0.json',
                              load=True)

print('Z2 topological invariant at kx = 0: {0}'.format(
    z2pack.invariant.z2(result_0)))

# Plot the WCC
fig, ax = plt.subplots(1, 1, sharey=True, figsize=(9, 5))
z2pack.plot.wcc(result_0, axis=ax)
plt.savefig('plots/plot.pdf', bbox_inches='tight')
