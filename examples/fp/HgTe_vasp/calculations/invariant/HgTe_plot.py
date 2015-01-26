#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    27.09.2014 15:39:41 CEST
# File:    HgTe_plot.py

import sys
sys.path.append("../../../../../")
import z2pack
sys.path.append('/home/greschd/programming')
from python_tools.plot_setup import *

import os
import numpy as np
import scipy.linalg as la

"""
HgTe plot
"""

if not os.path.exists('./results'):
    os.makedirs('./results')


string_dirs = [1, 1, 1, 1, 2, 2]
plane_pos_dirs = [2, 2, 0, 0, 1, 1]
plane_pos = [0, 0.5, 0, 0.5, 0, 0.5]

#~ def plot(i, wcc_index, string_index, suffix=None):
def plot(i, suffix=None):
    HgTe = z2pack.fp.System( ['INCAR', 'POSCAR', 'POTCAR', 'CHGCAR', 'wannier90.win'],
                            z2pack.fp.kpts.vasp,
                            "KPOINTS",
                            "build_" + str(i),
                            "mpirun $VASP_BIN/vasp.noncol >& log"
                        )

    pickle_file = 'results/res_'
    if suffix is not None:
        pickle_file += suffix
        pickle_file += '_'
    pickle_file += str(i) + '.txt'
    plane = HgTe.plane(string_dirs[i], plane_pos_dirs[i], plane_pos[i], pickle_file=pickle_file) 
    #~ plane.wcc_calc(iterator=[14], no_iter=True)

    res = plane.get_res()
    kpts = res['kpt']
    gap = res['gap']
    wcc = res['wcc']
    
    fig, ax = plt.subplots()
    #~ plane.plot(show=False, axis=ax)

    for j, w in enumerate(wcc):
        ax.plot([kpts[j]] * len(wcc[j]), wcc[j], 'r.', markersize=3.0)
    for j, g in enumerate(gap):
        ax.plot(kpts[j], g, 'b.', markersize=3.0)

        
    ax.set_title(r'Plane $k_{} = {}$, Invariant $\Delta = {}$'.format(plane_pos_dirs[i] + 1, plane_pos[i], plane.invariant()))
    ax.set_xlabel(r'$k_{}$'.format(4 - plane_pos_dirs[i] - string_dirs[i]))
    ax.set_ylabel(r'$x_{}$'.format(string_dirs[i] + 1))
    plot_file = './results/HgTe_'
    if suffix is not None:
        plot_file += suffix + '_'
    plot_file += str(i) + '.pdf'
    plt.savefig(plot_file, bbox_inches = 'tight')
    
if __name__ == "__main__":
    #~ indices = [1, 2, 3, 4, 5]
    for i in range(6):
        plot(i, suffix='fine')
        #~ plot(i)
    print("HgTe_plot.py")
