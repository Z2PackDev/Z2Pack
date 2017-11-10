"""Test volume calculations."""
# pylint: disable=redefined-outer-name,unused-wildcard-import,unused-argument

import os
import json
import pickle
import tempfile

import pytest
import msgpack
import numpy as np

import z2pack

from hm_systems import *
from tb_systems import *


@pytest.fixture(params=[2, 5, 11])
def num_lines(request):
    return request.param


@pytest.fixture(params=[2, 5, 11])
def num_surfaces(request):
    return request.param


@pytest.fixture(params=np.linspace(0.1, 0.4, 5))
def move_tol(request):
    return request.param


@pytest.fixture(params=[10**n for n in range(-4, -1)])
def gap_tol(request):
    return request.param


@pytest.fixture(params=[pickle, json, msgpack])
def serializer(request):
    return request.param


def assert_res_equal(result1, result2, ignore_wilson=False):
    """
    Checks that two results are equal.
    """
    assert result1.wcc == result2.wcc
    if not ignore_wilson:
        if hasattr(result1, 'wilson') or hasattr(result2, 'wilson'):
            assert all(np.isclose(result1.wilson, result2.wilson).flatten())
    assert result1.gap_size == result2.gap_size
    assert result1.gap_pos == result2.gap_pos
    assert result1.ctrl_states == result2.ctrl_states
    assert result1.convergence_report == result2.convergence_report


def test_simple(simple_system, simple_volume, num_surfaces, num_lines):
    """Test result of a simple surface calculation."""
    result = z2pack.volume.run(
        system=simple_system,
        volume=simple_volume,
        num_surfaces=num_surfaces,
        num_lines=num_lines
    )
    assert result.wcc == [[[0, 0]] * num_lines] * num_surfaces
    assert result.gap_size == [[1] * num_lines] * num_surfaces
    assert result.gap_pos == [[0.5] * num_lines] * num_surfaces
    assert result.ctrl_states == {}


# saving tests
def test_simple_save(num_lines, simple_system, simple_volume):
    """
    Test saving to a file during a simple volume calculation.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    result1 = z2pack.volume.run(
        system=simple_system,
        volume=simple_volume,
        num_lines=num_lines,
        save_file=temp_file.name
    )
    result2 = z2pack.io.load(temp_file.name, serializer=json)
    os.remove(temp_file.name)
    assert_res_equal(result1, result2)


# test restart
def test_restart(simple_system, simple_volume):
    """Test restarting a run from a result."""
    result1 = z2pack.volume.run(system=simple_system, volume=simple_volume)
    result2 = z2pack.volume.run(
        system=simple_system, volume=simple_volume, init_result=result1
    )
    assert_res_equal(result1, result2)


def test_restart_nocalc(simple_system, simple_volume):
    """
    Test that no additional calculations are performed when restarting from a (finished) saved calculation.
    """

    class Mock:
        @staticmethod
        def get_eig(*args, **kwargs):
            raise ValueError('This restart should not re-compute anything!')

    result1 = z2pack.volume.run(system=simple_system, volume=simple_volume)
    result2 = z2pack.volume.run(
        system=Mock(), volume=simple_volume, init_result=result1
    )
    assert_res_equal(result1, result2)


def test_invalid_restart(simple_system, simple_volume):
    """
    Test that you cannot pass the initial result explicitly and load from a file at the same time.
    """
    result = z2pack.volume.run(system=simple_system, volume=simple_volume)
    with pytest.raises(ValueError):
        z2pack.volume.run(
            system=simple_system,
            volume=simple_volume,
            init_result=result,
            load=True
        )


def test_file_restart(simple_system, simple_volume, serializer):
    """Test a restart from a save file."""
    with tempfile.NamedTemporaryFile() as temp_file:
        kwargs = dict(
            system=simple_system,
            volume=simple_volume,
            save_file=temp_file.name,
            serializer=serializer
        )
        result1 = z2pack.volume.run(**kwargs)
        result2 = z2pack.volume.run(load=True, load_quiet=False, **kwargs)
    assert_res_equal(result1, result2)


def test_load_inexisting(simple_system, simple_volume):
    """Test that trying to load from an inexisting file raises when load_quiet=False."""
    with pytest.raises(IOError):
        z2pack.volume.run(
            system=simple_system,
            volume=simple_volume,
            save_file='invalid_name',
            load_quiet=False,
            load=True,
            serializer=json
        )


def test_load_no_serializer(simple_system, simple_volume):
    """
    Test that loading from a file with no known extension or serializer given raises an error.
    """
    with pytest.raises(ValueError):
        z2pack.volume.run(
            system=simple_system,
            volume=simple_volume,
            save_file='invalid_name',
            load_quiet=False,
            load=True
        )


def test_load_no_filename(simple_system, simple_volume, serializer):
    """
    Test that trying to load raises an error if no filename is given.
    """
    with pytest.raises(ValueError):
        z2pack.volume.run(
            system=simple_system,
            volume=simple_volume,
            load=True,
            serializer=serializer
        )


def test_load_reference(simple_system, test_name, simple_volume, serializer):
    """
    Compare surface result to a reference from a file.
    """
    tag = test_name.split('/')[1]
    path = 'reference_results/volume_result_{}.'.format(
        tag
    ) + serializer.__name__
    result = z2pack.volume.run(system=simple_system, volume=simple_volume)
    if not os.path.isfile(path):
        z2pack.io.save(result, path, serializer=serializer)
        raise ValueError('File {} did not exist!'.format(path))
    else:
        assert_res_equal(result, z2pack.io.load(path, serializer=serializer))
        assert_res_equal(result, z2pack.io.load(path))


def test_invalid_save_path(simple_system, simple_volume):
    """
    Test that trying to save to an invalid path raises an error.
    """
    with pytest.raises(ValueError):

        def surface(*args, **kwargs):
            raise TypeError

        z2pack.volume.run(
            system=simple_system,
            volume=surface,
            save_file='some/invalid/path/file.json'
        )
