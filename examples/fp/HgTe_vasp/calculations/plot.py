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

def plot(name):
    with open('./results/' + name, 'r') as f:
        data = f.read().split('\n')[7:]

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

    del eigvals[100]

    fix, ax = plt.subplots()

    bands = np.array(eigvals).T
            
    x = np.arange(len(bands[0]))

    ax.set_xticks([0, 99, 198])
    ax.set_xticklabels(['X', 'G', 'L'])
    ax.set_xlabel(r'$k$')
    ax.set_ylabel(r'$E [\text{eV}]$', rotation='horizontal')
    ax.yaxis.set_label_coords(0, 1.05)
    ax.xaxis.set_label_coords(1, -0.09)
        
    occ = 18
    ax.set_xlim(0, len(eigvals) - 1)
    ax.set_ylim(min(bands[occ - 1]), max(bands[occ]))
    for band in bands:
        plt.plot(x, band, 'k')

    ax.plot(x, bands[occ - 1], 'r')

    ax.plot(x, bands[occ], 'b')

    plt.savefig('./plots/band_' + name + '.pdf')
    ax.cla()
        
if __name__ == "__main__":
    names = ['0', '0_5', '1', '1_5', '2', '2_5', '3', '3_5', '4',
            'm_0_5', 'm_1', 'm_1_5', 'm_2', 'm_2_5', 'm_3', 'm_3_5', 'm_4']

    for name in names:
        plot(name)


