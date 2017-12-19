#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import tempfile

import scipy.linalg as la
import numpy as np
import z2pack
from z2pack.espresso_symm_utils import *
import pytest


@pytest.fixture
def bi_symm_system(sample):
    def inner(build_dir):
        sample_dir = sample('espresso_symm')
        # Edit the paths to your Quantum Espresso and Wannier90 here
        shutil.copytree(
            os.path.join(sample_dir, 'scf'), os.path.join(build_dir, 'scf')
        )
        shutil.copytree(
            os.path.join(sample_dir, 'input'),
            os.path.join(build_dir, 'input')
        )
        qedir = '/home/tony/qe-6.2/bin'
        wandir = '/home/tony/wannier90-2.1.0'
        mpirun = ''
        pwcmd = 'pw.x '
        pw2wancmd = mpirun + qedir + '/pw2wannier90.x '
        wancmd = wandir + '/wannier90.x'

        z2cmd = (
            wancmd + ' bi -pp;' + pwcmd + '< bi.nscf.in >& pw.log;' +
            pw2wancmd + '< bi.pw2wan.in'
        )
        input_files = [
            os.path.join(sample_dir, 'input/') + name
            for name in [
                'bi.nscf.in', 'bi.pw2wan.in', 'bi.win', 'bi.sym',
                'Bi_MT_PBE.UPF'
            ]
        ]

        system = z2pack.fp.System(
            input_files=input_files,
            kpt_fct=[z2pack.fp.kpoint.qe, z2pack.fp.kpoint.wannier90_full],
            kpt_path=["bi.nscf.in", "bi.win"],
            command=z2cmd,
            executable='/bin/bash',
            build_folder=build_dir + '/build',
            mmn_path='bi.mmn',
            dmn_path='bi.dmn'
        )

        return system

    return inner


@pytest.mark.qe
def test_bi_symm(bi_symm_system, compare_wcc, sample):
    with tempfile.TemporaryDirectory() as build_dir:
        sample_dir = sample('espresso_symm')
        xml_path = os.path.join(sample_dir, 'scf/bi.xml')
        system = bi_symm_system(build_dir)
        symm_surf = suggest_symmetry_surfaces(xml_path)
        for i, s in enumerate(symm_surf):
            # Run the WCC calculations
            # The tolerances have to be turned off because this is not a physical system and the calculation does not converge
            # Generate .sym file
            gen_qe_symm_file(s.surface_lambda, xml_path, os.path.join(sample_dir, "input/bi.sym"))
            result = z2pack.surface.run(
                system=system,
                surface=s.surface_lambda,
                iterator=range(7, 9, 2),
                use_symm=True,
                pos_tol=None,
                gap_tol=None,
                move_tol=None
            )
            ew = np.unique(la.eig(s.symm)[0])
            for j, w in enumerate(ew):
                result_projected = result.symm_project(w, isym=1)
                compare_wcc(result_projected.wcc, tag="{}_proj_{}".format(i, j))
