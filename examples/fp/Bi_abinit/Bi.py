#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import z2pack
"""
Bismuth example
"""

if not os.path.exists('./results'):
    os.makedirs('./results')

# creating the System object
# the command (mpirun ...) will have to be replaced
Bi = z2pack.fp.System(
    input_files=[
        'input/Bi_nscf.files', 'input/Bi_nscf.in', 'input/wannier90.win'
    ],
    kpt_fct=z2pack.fp.kpoint.abinit,
    kpt_path='Bi_nscf.in',
    command=
    'mpirun -np 4 ~/software/abinit-7.10.5/src/98_main/abinit < Bi_nscf.files >& log',
    executable='/bin/bash'
)

# calculating the WCC
result_0 = z2pack.surface.run(
    system=Bi,
    surface=lambda s, t: [0, s / 2, t],
    save_file='./results/Bi_0.msgpack',
    load=True
)
result_1 = z2pack.surface.run(
    system=Bi,
    surface=lambda s, t: [0.5, s / 2, t],
    save_file='./results/Bi_1.msgpack',
    load=True
)
