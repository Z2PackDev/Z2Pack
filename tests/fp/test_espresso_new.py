"""
Tests for QE DFT calculations using the explicit interface.
"""
# pylint: disable=redefined-outer-name,unused-argument,protected-access

import os
import shutil
import tempfile

import pytest
import numpy as np

import z2pack


@pytest.fixture
def qe_system_new(sample):
    """
    Create QE system with explicit interface.
    """

    def inner(build_dir, num_wcc=None):
        sample_dir = sample('espresso_new')
        shutil.copytree(
            os.path.join(sample_dir, 'scf'), os.path.join(build_dir, 'scf')
        )
        input_files = [
            os.path.join(sample_dir, 'input/') + name
            for name in ['bi.nscf.in', 'bi.pw2wan.in', 'bi.win']
        ]

        qedir = '/home/greschd/software/qe-6.0/bin/'
        wandir = '/home/greschd/software/wannier90-2.1.0'
        mpirun = 'mpirun -np 4 '
        pwcmd = mpirun + qedir + '/pw.x '
        pw2wancmd = mpirun + qedir + '/pw2wannier90.x '
        wancmd = wandir + '/wannier90.x'
        z2cmd = (
            wancmd + ' bi -pp;' + pwcmd + '< bi.nscf.in >& pw.log;' + pw2wancmd
            + '< bi.pw2wan.in >& pw2wan.log;'
        )

        return z2pack.fp.System(
            input_files=input_files,
            kpt_fct=[
                z2pack.fp.kpoint.qe_explicit, z2pack.fp.kpoint.wannier90_full
            ],
            kpt_path=['bi.nscf.in', 'bi.win'],
            command=z2cmd,
            executable='/bin/bash',
            mmn_path='bi.mmn',
            build_folder=build_dir + '/build',
            num_wcc=num_wcc
        )

    return inner


SURFACE_FCTS = [
    lambda s, t: [0, s / 2, t], lambda s, t: [t, s, s],
    lambda s, t: [t, t, s / 2],
    z2pack.shape.Sphere(center=(0.1, 0.2, 0.3), radius=0.1)
]


@pytest.mark.qe
@pytest.mark.parametrize('surface_fct', SURFACE_FCTS)
def test_bismuth(qe_system_new, compare_wcc, surface_fct):
    """
    Test bismuth with explicit QE interface.
    """
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = qe_system_new(build_dir)
    save_file = os.path.join(build_dir, 'result.json')
    result = z2pack.surface.run(
        system=system,
        surface=surface_fct,
        num_lines=4,
        save_file=save_file,
        pos_tol=None,
        gap_tol=None,
        move_tol=None
    )
    compare_wcc(result.wcc)
    res2 = z2pack.io.load(save_file)
    assert np.isclose(result.wcc, res2.wcc).all()
    shutil.rmtree(build_dir)


@pytest.mark.qe
@pytest.mark.parametrize('surface_fct', [SURFACE_FCTS[0]])
def test_bismuth_wrong_num_wcc(qe_system_new, compare_wcc, surface_fct):
    """
    Test that bismuth run raises if the wrong num_wcc is set.
    """
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = qe_system_new(build_dir, num_wcc=12)

    with pytest.raises(ValueError):
        z2pack.surface.run(
            system=system,
            surface=surface_fct,
            num_lines=4,
            save_file=os.path.join(build_dir, 'result'),
            pos_tol=None,
            gap_tol=None,
            move_tol=None
        )


@pytest.mark.qe
@pytest.mark.parametrize('surface_fct', [SURFACE_FCTS[0]])
def test_bismuth_correct_num_wcc(qe_system_new, compare_wcc, surface_fct):
    """
    Test bismuth run with correct num_wcc set.
    """
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = qe_system_new(build_dir, num_wcc=10)

    save_file = os.path.join(build_dir, 'result.json')
    result = z2pack.surface.run(
        system=system,
        surface=surface_fct,
        num_lines=4,
        save_file=save_file,
        pos_tol=None,
        gap_tol=None,
        move_tol=None
    )
    compare_wcc(result.wcc)
    res2 = z2pack.io.load(save_file)
    assert np.isclose(result.wcc, res2.wcc).all()
    shutil.rmtree(build_dir)


def test_broken(qe_system_new):
    """
    Test that restart does not work when the fp.System is broken.
    """
    surface_fct = lambda s, t: [0, s, t]
    build_dir = tempfile.mkdtemp()
    system = qe_system_new(build_dir)
    save_file = os.path.join(build_dir, 'result.json')

    # breaking the system
    system._executable = 'echo foo'
    with pytest.raises(FileNotFoundError):
        z2pack.surface.run(
            system=system,
            surface=surface_fct,
            num_lines=3,
            save_file=save_file,
            pos_tol=None,
            gap_tol=None,
            move_tol=None
        )
    shutil.rmtree(build_dir)
