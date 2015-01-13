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
from scipy.interpolate import pchip


def plot_full():
    with open('EIGENVAL', 'r') as f:
        data = f.read().split('\n')[7:]

    points = ['X', 'G', 'L']
    points_set = [points]
    for i in range(len(points) - 1):
        points_set.append(points[i:i+2])

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

    step = 20
    eigvals.append(eigvals[100])
    intervals = [eigvals]
    intervals.extend([eigvals[i:i + step + 1] for i in range(0, len(eigvals), step)])

    fix, ax = plt.subplots()

    for i, eigvals_part in enumerate(intervals):
        bands = []
        for band in np.array(eigvals_part).T:
            bands.append(list(band))
            
        x = np.arange(len(bands[0]))
        xx = np.linspace(0, len(bands[0]), 10 * len(bands[0]))

        ax.set_xticks(range(0, len(bands[0]) + 1, 20))
        ax.set_xticklabels(points_set[i])
        ax.set_xlabel(r'$k$')
        ax.set_ylabel(r'$E [\text{eV}]$', rotation='horizontal')
        ax.yaxis.set_label_coords(0, 1.05)
        ax.xaxis.set_label_coords(1, -0.09)
        
        occ = 72
        ax.set_xlim(0, len(eigvals_part) - 1)
        ax.set_ylim(min(bands[occ - 1]), max(bands[occ]))
        for band in bands:
            interp = pchip(x, band)
            ax.plot(xx, interp(xx), 'k')
            #~ plt.plot(x, band, 'k')

        interp = pchip(x, bands[occ - 1])
        ax.plot(xx, interp(xx), 'r')

        interp = pchip(x, bands[occ])
        ax.plot(xx, interp(xx), 'b')

        plt.savefig('band_nosym_' + str(i) + '.pdf')
        ax.cla()

def plot_single(name, points):
    with open('results/' + name, 'r') as f:
        data = f.read().split('\n')[7:]

    points = [str(points[0]), str(points[1])]

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

    bands = []
    for band in np.array(eigvals).T:
        bands.append(list(band))

    for i in range(len(bands)):
        bands[i].append(bands[i][0])
        
    x = np.arange(len(bands[0]))
    xx = np.linspace(0, len(bands[0]), 10 * len(bands[0]))

    fix, ax = plt.subplots()
    ax.set_xticks([0, len(bands[0]) - 1])
    ax.set_xticklabels(points)
    ax.set_xlabel(r'$k$')
    ax.set_ylabel(r'$E [\text{eV}]$', rotation='horizontal')
    ax.yaxis.set_label_coords(0, 1.05)
    ax.xaxis.set_label_coords(1, -0.09)
    
    occ = 72

    ax.set_title(r'$\Delta E_\text{{min}} = {}$ eV'.format(min([bands[occ][i] - bands[occ - 1][i] for i in range(len(bands[occ]))])))
    ax.set_xlim(0, len(eigvals))
    ax.set_ylim(min(bands[occ - 1]), max(bands[occ]))


    lw = 0.2
    for band in bands:
        ax.plot(x, band, 'k', linewidth=lw)

    ax.plot(x, bands[occ - 1], 'r', linewidth=lw)
    ax.plot(x, bands[occ], 'b', linewidth=lw)

    plt.savefig(name + '.pdf')
    ax.cla()
    
if __name__ == "__main__":
    #~ plot_single('node', [[0.122, 0., 0.], [0.122, 1., 0.]])
    plot_full
    print("plot.py")
    
