#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    24.03.2016 16:00:14 CET
# File:    test_abinit.py

import shutil
import tempfile

import pytest
import numpy as np

import z2pack

@pytest.fixture
def abinit_system():
    def inner(build_dir):
        input_files = ['samples/abinit/' + name for name in [
            'Bi_nscf.files', 'Bi_nscf.in', 'wannier90.win', '83bi.5.hgh', 'Bi_scf_o_DEN'
        ]]
        return z2pack.fp.System(
            input_files=input_files,
            kpt_fct=z2pack.fp.kpoint.abinit,
            kpt_path="Bi_nscf.in",
            command="mpirun -np 4 abinit < Bi_nscf.files >& log",
            executable='/bin/bash',
            build_folder=build_dir + '/build'
        )
    return inner

surface_fcts = [
    lambda s, t: [0, s / 2, t],
    lambda s, t: [t, s, s]
]

@pytest.mark.abinit
@pytest.mark.parametrize('surface_fct', surface_fcts)
def test_bismuth(abinit_system, compare_data, surface_fct):
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = abinit_system(build_dir)
    result = z2pack.surface.run(
        system=system,
        surface=surface_fct,
        num_strings=4,
        pos_tol=None,
        gap_tol=None,
        move_tol=None
    )
    compare_wcc(result.wcc)
    shutil.rmtree(build_dir)
