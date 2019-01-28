"""Test for symmetry projection of first principles systems."""

# pylint: disable=missing-docstring,redefined-outer-name

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join
import shutil
import tempfile
import scipy.linalg as la
import numpy as np
import pytest

import z2pack
from z2pack.symm_utils.espresso import generate_qe_sym_file, suggest_symmetry_surfaces


@pytest.fixture
def bi_symm_system(sample, qe_6_2_dir, wannier_2_1_dir):
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
        mpirun = ''
        pwcmd = join(qe_6_2_dir, 'pw.x') + ' '
        pw2wancmd = mpirun + join(qe_6_2_dir, 'pw2wannier90.x') + ' '
        wancmd = join(wannier_2_1_dir, 'wannier90.x') + ' '

        z2cmd = (
            wancmd + ' bi -pp;' + pwcmd + '< bi.nscf.in;' + pw2wancmd +
            '< bi.pw2wan.in'
        )
        input_files = [
            os.path.join(sample_dir, 'input/') + name for name in [
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
        for i, (surf, symm) in enumerate(symm_surf):
            # Run the WCC calculations
            # The tolerances have to be turned off because this is not a physical system and the calculation does not converge
            # Generate .sym file
            generate_qe_sym_file(
                surf, xml_path, os.path.join(sample_dir, "input/bi.sym")
            )
            result = z2pack.surface.run(
                system=system,
                surface=surf,
                iterator=range(7, 9, 2),
                use_symm=True,
                pos_tol=None,
                gap_tol=None,
                move_tol=None
            )
            ew = np.unique(la.eig(symm)[0])
            for j, w in enumerate(ew):
                result_projected = result.symm_project(w, isym=1)
                compare_wcc(
                    result_projected.wcc, tag="{}_proj_{}".format(i, j)
                )
