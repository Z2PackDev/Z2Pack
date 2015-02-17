#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    14.08.2014 12:18:25 CEST
# File:    BiSe.py

import sys
sys.path.append("../../../")
import z2pack

import os

"""
Bismuth Selenide example
"""

if __name__ == "__main__":

    if not os.path.exists('./results'):
        os.makedirs('./results')

    # creating the z2pack.abinit object
    Bi2Se3 = z2pack.fp.System(["Bi2Se3_nscf.files", "Bi2Se3_nscf.in", "wannier90.win" ],
                            z2pack.fp.kpts.abinit,
                            "Bi2Se3_nscf.in",
                            "abinit < Bi2Se3_nscf.files >& log",
                            executable='/bin/bash'
                            )

    # surface at k1=0
    surface_0 = Bi2Se3.surface(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = 'results/Bi2Se3_0.txt')
    surface_0.wcc_calc()

    # surface at k1=Pi
    surface_1 = Bi2Se3.surface(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = 'results/Bi2Se3_1.txt')
    surface_1.wcc_calc()
