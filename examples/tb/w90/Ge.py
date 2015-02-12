#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    squarelattice.py

import os
import sys
sys.path.append("../../../")
import z2pack.tb as tb

import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

def calculate(settings):
    # Creating the Hamilton from the Wannier90 output file
    H = tb.w90.Hamilton('wannier90_hr.dat', 'wannier90.wout', 8)
    tb_system = tb.System(H)
    tb_surface = tb_system.surface(lambda kx: [kx / 2., 0, 0], [0, 1, 0])
    tb_surface.wcc_calc(verbose=True, no_iter=False)

def plot():
    H = tb.w90.Hamilton('wannier90_hr.dat', 'wannier90.wout', 8)
    tb_system = tb.System(H)
    tb_surface = tb_system.surface(lambda kx: [kx / 2., 0, 0], [0, 1, 0])
    
    tb_surface.load()
    fig = plt.figure()
    ax = fig.add_subplot()
    tb_surface.plot(axis=ax, show=False)
    plt.savefig('./results/Ge.pdf', bbox_inches = 'tight')

    # Printing the results
    print("Z2 invariant: {}".format(tb_surface.invariant()))

def bandstructure():
    system = tb.w90.Hamilton('wannier90_hr.dat', 'wannier90.wout', 8)
    H = system.create_hamiltonian()

    eigenvalues = []
    for x in np.linspace(0.5, 0, 30, endpoint=False):
        eigenvalues.append(sorted(la.eig(H([x, 0, 0]))[0].real))

    for x in np.linspace(0, 0.5, 31):
        eigenvalues.append(sorted(la.eig(H([0, x, x]))[0].real))

    for band in np.array(eigenvalues).T:
        plt.plot(np.arange(len(band)), band)
    plt.show()

if __name__ == "__main__":
    if not os.path.exists('./results'):
        os.makedirs('./results')

    settings = {'verbose': True, 'iterator': range(12, 37, 2)}
    calculate(settings)
    plot()
    #~ bandstructure()
    
