#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.12.2014 21:15:37 CET
# File:    plot_bands.py

from __future__ import division, print_function


import sys
sys.path.append('/home/greschd/programming')
from python_tools.plot_setup import *
import numpy as np
import matplotlib.pyplot as plt

with open('./bandstructure/HgTe_nscf_o_EIG', 'r') as f:
    data = f.read().split('\n')

for i, line in enumerate(data):
    if('eV' in line):
        data = data[i + 1:]

eigvals = []
tmp = []
first = True
for line in data:
    if('kpt' in line):
        if not first:
            eigvals.append(tmp)
            tmp = []
        else:
            first = False
    else:
        tmp.extend([float(x) for x in filter(None, line.split(' '))])

eigvals.append(tmp)

    
bands = np.array(eigvals).T

x = np.arange(len(bands[0]))

points = ['X', r'$\Gamma$', 'L']
fix, ax = plt.subplots()
ax.set_xticks([0, 20, 40])
ax.set_xticklabels(points)
ax.set_xlabel(r'$k$')
ax.set_ylabel(r'$E [\text{eV}]$', rotation='horizontal')
ax.yaxis.set_label_coords(0, 1.05)
ax.xaxis.set_label_coords(1, -0.09)

occ = 18

ax.set_title(r'$\Delta E_\text{{min}} = {}$ eV, gap $ = {}$ eV'.format(min([bands[occ][i] - bands[occ - 1][i] for i in range(len(bands[occ]))]), min(bands[occ]) - max(bands[occ - 1])))
ax.set_xlim(0, len(eigvals))
ax.set_ylim(min(bands[occ - 1]), max(bands[occ]))


lw = 0.2
for band in bands:
    ax.plot(x, band, 'k', linewidth=lw)

ax.plot(x, bands[occ - 1], 'r', linewidth=lw)
ax.plot(x, bands[occ], 'b', linewidth=lw)

plt.savefig('./results/band.pdf')
ax.cla()

if __name__ == "__main__":
    print("plot_bands.py")
    
