#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Gabriel Autès, Dominik Gresch
# File:    run.py

import os

import z2pack
import matplotlib.pyplot as plt

qedir="/home/greschd/software/espresso-5.3.0/bin"
mpirun="mpirun -np 4 "
pwcmd=mpirun+qedir+"/pw.x " 
pw2z2cmd=qedir+"/pw2z2pack.x "
z2cmd=pwcmd+"< bi.nscf.in >& pw.log;"+pw2z2cmd+"< bi.pw2z2.in >& pw2z2.log;"

# Settings used for surface.run() Feel free to play around with the different
# options.
settings = {
    'num_lines': 41,
    'pos_tol': 1e-2,
    'gap_tol': 0.2,
    'move_tol': 0.3,
    'iterator': range(10, 36, 4),
    'min_neighbour_dist': 2e-2
}

# run the scf calculation
os.makedirs('scf', exist_ok=True)
if not os.path.isfile('./scf/Bi.save/charge-density.dat'):
    print("Running the scf calculation")
    shutil.copy('input/bi.scf.in', 'scf')
    subprocess.check_output(pwcmd + " < bi.scf.in > scf.out", shell=True, cwd='scf')
    
# creating the z2pack.fp object
bi = z2pack.fp.System(  
    input_files=[
        os.path.join('input', fn) for fn in 
        ["bi.nscf.in", "bi.pw2z2.in"]
    ],
    kpt_fct=[z2pack.fp.kpts.qe],
    kpt_path=["bi.nscf.in"],
    command=z2cmd,
    executable='/bin/bash',
    mmn_path='bi.mmn'
)

# running the z2pack calculation
res_1 = z2pack.surface.run(
    system=bi,
    surface=lambda s, t: [s / 2, 0, t],
    save_file='results/res_1.json',
    load=True
    **settings
)

res_2 = z2pack.surface.run(
    system=bi,
    surface=lambda s, t: [s / 2, 0.5, t],
    save_file='results/res_2.json',
    load=True
    **settings
)

# creating the plot
fig=plt.figure()

ax=fig.add_subplot(1,2,1)
z2pack.plot.wcc(res_1, axis=ax)

ax=fig.add_subplot(1,2,2)
z2pack.plot.wcc(res_2, axis=ax)

plt.savefig('results/wcc.pdf',bbox_inches='tight')
