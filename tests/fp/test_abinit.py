"""
Tests for ABINIT DFT calculations.
"""
# pylint: disable=redefined-outer-name

import os
import shutil
import tempfile

import pytest

import z2pack


@pytest.fixture
def abinit_system(sample):
    """
    Create ABINIT system.
    """
    def inner(build_dir):
        sample_dir = sample('abinit')
        input_files = [
            os.path.join(sample_dir, name) for name in [
                'Bi_nscf.files', 'Bi_nscf.in', 'wannier90.win', '83bi.5.hgh',
                'Bi_scf_o_DEN'
            ]
        ]
        return z2pack.fp.System(
            input_files=input_files,
            kpt_fct=z2pack.fp.kpoint.abinit,
            kpt_path="Bi_nscf.in",
            command="mpirun -np 4 abinit < Bi_nscf.files >& log",
            executable='/bin/bash',
            build_folder=os.path.join(build_dir, 'build')
        )

    return inner


SURFACE_FCTS = [lambda s, t: [0, s / 2, t], lambda s, t: [t, s, s]]


@pytest.mark.abinit
@pytest.mark.parametrize('surface_fct', SURFACE_FCTS)
def test_bismuth(abinit_system, compare_wcc, surface_fct):
    """
    Test bismuth run with ABINIT.
    """
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = abinit_system(build_dir)
    result = z2pack.surface.run(
        system=system,
        surface=surface_fct,
        num_lines=4,
        pos_tol=None,
        gap_tol=None,
        move_tol=None
    )
    compare_wcc(result.wcc)
    shutil.rmtree(build_dir)
