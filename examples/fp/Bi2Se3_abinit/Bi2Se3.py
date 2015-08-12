#!/usr/bin/env python
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
<<<<<<< HEAD
    Bi2Se3 = z2pack.fp.System(['input/' + name for name in ["Bi2Se3_nscf.files", "Bi2Se3_nscf.in", "w90.win", "w.win"]],
                            z2pack.fp.kpts.abinit,
                            "Bi2Se3_nscf.in",
                            "mpirun $ABINIT < Bi2Se3_nscf.files >& log",
                            executable='/bin/bash'
                            )
=======
    Bi2Se3 = z2pack.fp.System(
        ['input/' + name for name in ["Bi2Se3_nscf.files", "Bi2Se3_nscf.in", "wannier90.win" ]],
        z2pack.fp.kpts.abinit,
        "Bi2Se3_nscf.in",
        "mpirun -np 7 abinit < Bi2Se3_nscf.files >& log",
        executable='/bin/bash'
    )
>>>>>>> 5a50e0d8de3f1a4e3f5204df92ad7db1704eeb71

    # surface at k1=0
    surface_0 = Bi2Se3.surface(lambda t: [0, t / 2, 0], [0, 0, 1], pickle_file = 'results/Bi2Se3_0.txt')
    surface_0.wcc_calc()

    # surface at k1=Pi
    surface_1 = Bi2Se3.surface(lambda t: [0.5, t / 2, 0], [0, 0, 1], pickle_file = 'results/Bi2Se3_1.txt')
    surface_1.wcc_calc()
