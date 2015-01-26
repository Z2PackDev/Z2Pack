#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.12.2014 23:39:05 CET
# File:    plot.py

import sys
sys.path.append('/home/greschd/programming')
from python_tools.plot_setup import *

import numpy as np
import matplotlib.pyplot as plt


def plot():
    with open('EIGENVAL', 'r') as f:
        data = f.read().split('\n')[7:]

    points = ['X', 'G', 'L']

    kpts = []
    eigvals = []

    tmp = []
    new = True
    for line in data:
        if(len(line) < 5):
            eigvals.append(tmp)
            tmp = []
            new = True
        else:
            if(new):
                new = False
            else:
                tmp.append(float(filter(None, line.split(' '))[1]))

    #~ step = 20
    del eigvals[19]
    #~ eigvals.append(eigvals[100])

    fix, ax = plt.subplots()

    bands = []
    for band in np.array(eigvals).T:
        bands.append(list(band))
        
    x = np.arange(len(bands[0]))
    xx = np.linspace(0, len(bands[0]), 10 * len(bands[0]))

    ax.set_xticks(range(0, len(bands[0]) + 1, 19))
    ax.set_xticklabels(points)
    ax.set_xlabel(r'$k$')
    ax.set_ylabel(r'$E [\text{eV}]$', rotation='horizontal')
    ax.yaxis.set_label_coords(0, 1.05)
    ax.xaxis.set_label_coords(1, -0.09)
    
    occ = 18
    
    ax.set_title(r'$\Delta E_\text{{min}} = {:.6f}$ eV, $E_\text{{g}} = {:.6f}$ eV'.format((min([bands[occ][i] - bands[occ - 1][i] for i in range(len(bands[occ]))])), min(bands[occ] - max(bands[occ - 1]))))
    ax.set_xlim(0, len(eigvals) - 1)
    ax.set_ylim(min(bands[occ - 1]), max(bands[occ]))
    for band in bands:
        plt.plot(x, band, 'k')

    ax.plot(x, bands[occ - 1], 'r')
    ax.plot(x, bands[occ], 'b')

    plt.savefig('band.pdf')
    ax.cla()

    
if __name__ == "__main__":
    plot()
    print("plot.py")
    
