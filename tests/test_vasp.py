#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    21.07.2016 15:07:47 CEST
# File:    test_vasp.py


import shutil
import tempfile

import pytest
import numpy as np

import z2pack

@pytest.fixture
def vasp_system():
    def inner(build_dir):
        input_files = ['samples/vasp/' + name for name in ['CHGCAR', 'INCAR', 'POSCAR', 'POTCAR', 'wannier90.win']]
        return z2pack.fp.System(
            input_files=input_files,
            kpt_fct=z2pack.fp.kpoint.vasp,
            kpt_path='KPOINTS',
            command='mpirun $VASP >& log',
            build_folder=build_dir
        )
    return inner

surface_fcts = [
    lambda s, t: [0, s / 2, t],
    lambda s, t: [t, s, s]
]

@pytest.mark.vasp
@pytest.mark.parametrize('surface_fct', surface_fcts)
def test_bismuth(vasp_system, compare_wcc, surface_fct):
    # don't want to remove it if the test failed
    build_dir = tempfile.mkdtemp()
    system = vasp_system(build_dir)
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
    
invalid_surface_fcts = [
    lambda s, t: [0, s / 2, t + 0.1],
    lambda s, t: [s, t]
]

@pytest.mark.parametrize('surface_fct', invalid_surface_fcts)
def test_invalid_surface(vasp_system, surface_fct):
    build_dir=tempfile.mkdtemp()
    system = vasp_system(build_dir)
    with pytest.raises(ValueError):
        result = z2pack.surface.run(
            system=system,
            surface=surface_fct
        )

