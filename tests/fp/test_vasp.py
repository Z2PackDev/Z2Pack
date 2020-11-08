"""
Tests for VASP DFT calculations.
"""
# pylint: disable=redefined-outer-name

import os
import shutil
import tempfile

import pytest
import z2pack


@pytest.fixture
def vasp_system(sample):
    """
    Create a VASP system.
    """
    def inner(build_dir):
        samples_dir = sample('vasp')
        input_files = [
            os.path.join(samples_dir, name) for name in
            ['CHGCAR', 'INCAR', 'POSCAR', 'POTCAR', 'wannier90.win']
        ]
        return z2pack.fp.System(
            input_files=input_files,
            kpt_fct=z2pack.fp.kpoint.vasp,
            kpt_path='KPOINTS',
            command='mpirun $VASP >& log',
            build_folder=build_dir
        )

    return inner


@pytest.fixture
def vasp_system_no_potcar(sample):
    """
    Create a VASP system without the POTCAR file.
    """
    def inner(build_dir):
        samples_dir = sample('vasp')
        input_files = [
            os.path.join(samples_dir, name)
            for name in ['CHGCAR', 'INCAR', 'POSCAR', 'wannier90.win']
        ]
        return z2pack.fp.System(
            input_files=input_files,
            kpt_fct=z2pack.fp.kpoint.vasp,
            kpt_path='KPOINTS',
            command='mpirun $VASP >& log',
            build_folder=build_dir
        )

    return inner


SURFACE_FCTS = [lambda s, t: [0, s / 2, t], lambda s, t: [t, s, s]]


@pytest.mark.vasp
@pytest.mark.parametrize('surface_fct', SURFACE_FCTS)
def test_bismuth(vasp_system, compare_wcc, surface_fct):
    """
    Test bismuth calculation.
    """
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = vasp_system(build_dir)
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


INVALID_SURFACE_FCTS = [lambda s, t: [0, s / 2, t + 0.1], lambda s, t: [s, t]]


@pytest.mark.parametrize('surface_fct', INVALID_SURFACE_FCTS)
def test_invalid_surface(vasp_system_no_potcar, surface_fct):
    """
    Test that trying to run invalid surface functions raises.
    """
    build_dir = tempfile.mkdtemp()
    system = vasp_system_no_potcar(build_dir)
    with pytest.raises(ValueError):
        z2pack.surface.run(system=system, surface=surface_fct)
