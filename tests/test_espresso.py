#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    24.03.2016 15:26:43 CET
# File:    test_espresso.py

import shutil
import tempfile

import pytest
import numpy as np

import z2pack

@pytest.fixture
def qe_system():
    def inner(build_dir):
        shutil.copytree('samples/espresso/scf', build_dir + '/scf')
        input_files = ['samples/espresso/input/' + name for name in [
            'bi.nscf.in', 'bi.pw2wan.in', 'bi.win'
        ]]

        qedir = '/home/greschd/software/espresso-5.1.2/bin/'
        wandir = '/home/greschd/software/wannier90-1.2'
        mpirun = 'mpirun -np 4 '
        pwcmd = mpirun + qedir + '/pw.x '
        pw2wancmd = mpirun + qedir + '/pw2wannier90.x '
        wancmd = wandir + '/wannier90.x'
        z2cmd = (
            wancmd + ' bi -pp;' +
            pwcmd + '< bi.nscf.in >& pw.log;' +
            pw2wancmd + '< bi.pw2wan.in >& pw2wan.log;'
        )
        return z2pack.fp.System(
            input_files=input_files,
            kpt_fct=[z2pack.fp.kpoint.qe, z2pack.fp.kpoint.wannier90],
            kpt_path=['bi.nscf.in','bi.win'],
            command=z2cmd,
            executable='/bin/bash',
            mmn_path='bi.mmn',
            build_folder=build_dir + '/build'
        )
    return inner

surface_fcts = [
    lambda s, t: [0, s / 2, t],
    lambda s, t: [t, s, s],
    lambda s, t: [t, t, s / 2]
]

@pytest.mark.qe
@pytest.mark.parametrize('surface_fct', surface_fcts)
def test_bismuth(qe_system, compare_data, surface_fct):
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = qe_system(build_dir)
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
