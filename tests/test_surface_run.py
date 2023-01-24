"""Test surface calculations."""
# pylint: disable=redefined-outer-name,unused-wildcard-import,too-many-arguments

import json
import os
import pickle
import tempfile

import msgpack
import numpy as np
import pytest
import z2pack

from hm_systems import *
from tb_systems import *


@pytest.fixture(params=range(5, 11, 2))
def num_lines(request):
    return request.param


@pytest.fixture(params=[0.1, 0.175, 0.25, 0.325, 0.4])
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
        if hasattr(result1, "wilson") or hasattr(result2, "wilson"):
            assert all(np.isclose(result1.wilson, result2.wilson).flatten())
    assert result1.gap_size == result2.gap_size
    assert result1.gap_pos == result2.gap_pos
    assert result1.ctrl_states == result2.ctrl_states
    assert result1.convergence_report == result2.convergence_report


def test_simple(simple_system, simple_surface, num_lines):
    """Test result of a simple surface calculation."""
    result = z2pack.surface.run(system=simple_system, surface=simple_surface, num_lines=num_lines)
    assert result.wcc == [[0, 0]] * num_lines
    assert result.gap_size == [1] * num_lines
    assert result.gap_pos == [0.5] * num_lines
    assert result.ctrl_states == {}


def test_neighbour_dist(weyl_system, weyl_surface):
    """
    Test that no additional neighbours are added if the min_neighbour_dist is reached.
    """
    result = z2pack.surface.run(
        system=weyl_system,
        surface=weyl_surface,
        num_lines=11,
        min_neighbour_dist=0.09,
        move_tol=0.0,
        gap_tol=1.0,
    )
    assert len(result.wcc) == 11


def test_weyl(
    compare_data,
    compare_equal,
    pos_tol,
    gap_tol,
    move_tol,
    num_lines,
    weyl_system,
    weyl_surface,
):
    """Test Weyl node system."""
    result = z2pack.surface.run(
        system=weyl_system,
        surface=weyl_surface,
        num_lines=num_lines,
        move_tol=move_tol,
        gap_tol=gap_tol,
        pos_tol=pos_tol,
    )
    compare_data(lambda l1, l2: all(np.isclose(l1, l2).flatten()), result.wcc)
    compare_equal(result.convergence_report, tag="_report")


def test_tb(
    compare_wcc,
    compare_equal,
    pos_tol,
    gap_tol,
    move_tol,
    num_lines,
    tb_system,
    tb_surface,
):
    """Test tight-binding model."""
    result = z2pack.surface.run(
        system=tb_system,
        surface=tb_surface,
        num_lines=num_lines,
        move_tol=move_tol,
        gap_tol=gap_tol,
        pos_tol=pos_tol,
    )
    compare_wcc(result.wcc)
    compare_equal(result.convergence_report, tag="_report")


# saving tests
def test_simple_save(num_lines, simple_system, simple_surface):
    """
    Test saving to a file during a simple surface calculation.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    result1 = z2pack.surface.run(
        system=simple_system,
        surface=simple_surface,
        num_lines=num_lines,
        save_file=temp_file.name,
    )
    result2 = z2pack.io.load(temp_file.name, serializer=json)
    os.remove(temp_file.name)
    assert_res_equal(result1, result2)


def test_weyl_save(pos_tol, gap_tol, move_tol, num_lines, weyl_system, weyl_surface):
    """Test saving to a file with the Weyl system."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    result1 = z2pack.surface.run(
        system=weyl_system,
        surface=weyl_surface,
        num_lines=num_lines,
        move_tol=move_tol,
        gap_tol=gap_tol,
        pos_tol=pos_tol,
        save_file=temp_file.name,
    )
    result2 = z2pack.io.load(temp_file.name, serializer=json)
    os.remove(temp_file.name)
    assert_res_equal(result1, result2)


def test_tb_save(pos_tol, gap_tol, move_tol, num_lines, tb_system, tb_surface):
    """Test saving to a file with the tight-binding system."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    result1 = z2pack.surface.run(
        system=tb_system,
        surface=tb_surface,
        num_lines=num_lines,
        move_tol=move_tol,
        gap_tol=gap_tol,
        pos_tol=pos_tol,
        save_file=temp_file.name,
    )
    result2 = z2pack.io.load(temp_file.name, serializer=json)
    os.remove(temp_file.name)
    assert_res_equal(result1, result2)


# test restart
def test_restart(simple_system, simple_surface):
    """Test restarting a run from a savefile."""
    result1 = z2pack.surface.run(system=simple_system, surface=simple_surface)
    result2 = z2pack.surface.run(system=simple_system, surface=simple_surface, init_result=result1)
    assert_res_equal(result1, result2)


def test_restart_nocalc(simple_system, simple_surface):
    """
    Test that no additional calculations are performed when restarting from a (finished) saved calculation.
    """

    class Mock:
        @staticmethod
        def get_eig(*args, **kwargs):
            raise ValueError("This restart should not re-compute anything!")

    result1 = z2pack.surface.run(system=simple_system, surface=simple_surface)
    result2 = z2pack.surface.run(system=Mock(), surface=simple_surface, init_result=result1)
    assert_res_equal(result1, result2)


def test_restart_2(weyl_system, weyl_surface):
    """Test restart from a reduced precision run."""
    result1 = z2pack.surface.run(system=weyl_system, surface=weyl_surface)
    result2 = z2pack.surface.run(
        system=weyl_system,
        surface=weyl_surface,
        pos_tol=0.5,
        gap_tol=1e-1,
        move_tol=0.5,
        num_lines=6,
    )
    result2 = z2pack.surface.run(system=weyl_system, surface=weyl_surface, init_result=result2)
    assert_res_equal(result1, result2)


def test_invalid_restart(simple_system, simple_surface):
    """
    Test that you cannot pass the initial result explicitly and load from a file at the same time.
    """
    result = z2pack.surface.run(system=simple_system, surface=simple_surface)
    with pytest.raises(ValueError):
        z2pack.surface.run(
            system=simple_system, surface=simple_surface, init_result=result, load=True
        )


def test_file_restart(simple_system, simple_surface, serializer):
    """Test a restart from a save file."""
    with tempfile.NamedTemporaryFile() as temp_file:
        kwargs = dict(
            system=simple_system,
            surface=simple_surface,
            save_file=temp_file.name,
            serializer=serializer,
        )
        result1 = z2pack.surface.run(**kwargs)
        result2 = z2pack.surface.run(load=True, **kwargs)
    assert_res_equal(result1, result2)


def test_load_inexisting(simple_system, simple_surface):
    """Test that trying to load from an inexisting file raises when load_quiet=False."""
    with pytest.raises(IOError):
        z2pack.surface.run(
            system=simple_system,
            surface=simple_surface,
            save_file="invalid_name",
            load_quiet=False,
            load=True,
            serializer=json,
        )


def test_load_no_serializer(simple_system, simple_surface):
    """
    Test that loading from a file with no known extension or serializer given raises an error.
    """
    with pytest.raises(ValueError):
        z2pack.surface.run(
            system=simple_system,
            surface=simple_surface,
            save_file="invalid_name",
            load_quiet=False,
            load=True,
        )


def test_load_no_filename(simple_system, simple_surface, serializer):
    """
    Test that trying to load raises an error if no filename is given.
    """
    with pytest.raises(ValueError):
        z2pack.surface.run(
            system=simple_system,
            surface=simple_surface,
            load=True,
            serializer=serializer,
        )


def test_load_reference(simple_system, test_name, simple_surface, serializer):
    """
    Compare surface result to a reference from a file.
    """
    tag = test_name.split("/")[1]
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "reference_results",
        f"result_{tag}." + serializer.__name__,
    )
    result = z2pack.surface.run(system=simple_system, surface=simple_surface)
    if not os.path.isfile(path):
        z2pack.io.save(result, path, serializer=serializer)
        raise ValueError(f"File {path} did not exist!")
    assert_res_equal(result, z2pack.io.load(path, serializer=serializer))
    assert_res_equal(result, z2pack.io.load(path))


def test_load_reference_legacy_v1(simple_system, test_name, simple_surface, serializer):
    """
    Compare surface result to a reference from a file. The reference results are from Z2Pack version 2.1, where the OverlapLineData does not exist.
    """
    # legacy results created with pickle cannot be loaded
    if serializer is pickle:
        return
    tag = test_name.split("/")[1]
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "reference_results",
        f"result_{tag}." + serializer.__name__,
    )
    result = z2pack.surface.run(system=simple_system, surface=simple_surface)
    if not os.path.isfile(path):
        z2pack.io.save(result, path, serializer=serializer)
        raise ValueError(f"File {path} did not exist!")
    for saved_res in [
        z2pack.io.load(path, serializer=serializer),
        z2pack.io.load(path),
    ]:
        assert_res_equal(result, saved_res, ignore_wilson=not hasattr(saved_res, "wilson"))


def test_invalid_save_path(simple_system, simple_surface):
    """
    Test that trying to save to an invalid path raises an error.
    """
    with pytest.raises(ValueError):

        def surface(*args, **kwargs):
            raise TypeError

        z2pack.surface.run(
            system=simple_system,
            surface=surface,
            save_file="some/invalid/path/file.json",
        )
