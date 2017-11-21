"""Tests for line calculations."""
# pylint: disable=unused-wildcard-import,redefined-outer-name

import os
import json
import tempfile

import pytest
import numpy as np
import z2pack
from z2pack._utils import _get_max_move

from hm_systems import *
from tb_systems import *


def normalize_convergence_report(report):
    """
    Converts values in convergence report from np.bool_ to bool.
    """
    return {key: bool(val) for key, val in report.items()}


def test_trivial_run(simple_system, simple_line, compare_equal):
    """Test simple line run."""
    result = z2pack.line.run(system=simple_system, line=simple_line)
    assert result.wcc == [0, 0]
    assert result.gap_pos == 0.5
    assert result.gap_size == 1
    assert result.ctrl_states['StepCounter'] == 10
    assert result.ctrl_states['PosCheck'] == dict(max_move=0, last_wcc=[0, 0])
    compare_equal(normalize_convergence_report(result.convergence_report))


def test_weyl(weyl_system, weyl_line, compare_data):
    """Test line run for Weyl system."""
    result = z2pack.line.run(system=weyl_system, line=weyl_line)
    compare_data(lambda r1, r2: all(np.isclose(r1, r1).flatten()), result.wcc)

def test_tb(compare_wcc, compare_equal, pos_tol, tb_system, tb_line):
    result = z2pack.line.run(
        system=tb_system,
        line=tb_line,
        pos_tol=pos_tol
    )
    compare_wcc(result.wcc)
    compare_equal(result.convergence_report, tag='_report')

def test_tb_convention(pos_tol, tb_system, tb_model, tb_line):
    result1 = z2pack.line.run(
        system=tb_system,
        line=tb_line,
        pos_tol=pos_tol
    )
    tb_system_convention1 = z2pack.hm.System(
        hamilton=lambda k: tb_model.hamilton(k, convention=1),
        convention=1
    )
    result2 = z2pack.line.run(
        system=tb_system_convention1,
        line=tb_line,
        pos_tol=pos_tol
    )
    assert _get_max_move(result1.wcc, result2.wcc) < 1e-8

def test_no_pos_tol(simple_system, simple_line, compare_equal):
    """Test simple line run without pos_tol check."""
    result = z2pack.line.run(
        system=simple_system, line=simple_line, pos_tol=None
    )
    assert result.wcc == [0, 0]
    assert result.gap_pos == 0.5
    assert result.gap_size == 1
    assert result.ctrl_states['StepCounter'] == 8
    with pytest.raises(KeyError):
        result.ctrl_states['PosCheck']  # pylint: disable=pointless-statement
    compare_equal(normalize_convergence_report(result.convergence_report))


def test_pos_tol(weyl_system, weyl_line, pos_tol, compare_equal):
    """Test simple line run with different pos_tol values."""
    result = z2pack.line.run(
        system=weyl_system, line=weyl_line, pos_tol=pos_tol
    )
    compare_equal(result.ctrl_states['StepCounter'])
    compare_equal(
        normalize_convergence_report(result.convergence_report), tag='_report'
    )


def test_iterator(simple_system, simple_line, compare_equal):
    """Test simple line run with special iterator value."""
    result = z2pack.line.run(
        system=simple_system, line=simple_line, iterator=[5, 7, 9]
    )
    assert result.ctrl_states['StepCounter'] == 7
    compare_equal(normalize_convergence_report(result.convergence_report))


def test_iterator_2(weyl_system, compare_equal):
    """Test simple line run with special iterator value."""
    result = z2pack.line.run(
        system=weyl_system,
        line=weyl_line(0.1),
        iterator=[4, 12, 21],
        pos_tol=1e-12
    )
    assert result.ctrl_states['StepCounter'] == 21
    compare_equal(normalize_convergence_report(result.convergence_report))


def test_iterator_3(simple_system, simple_line, compare_equal):
    """
    Test simple line run with special iterator value and no pos_tol check.
    """
    result = z2pack.line.run(
        system=simple_system,
        line=simple_line,
        iterator=[4, 12, 21],
        pos_tol=None
    )
    assert result.ctrl_states['StepCounter'] == 4
    compare_equal(normalize_convergence_report(result.convergence_report))


def assert_res_equal(result1, result2):
    """
    Check that two line results are equal.
    """
    assert result1.wcc == result2.wcc
    assert result1.gap_pos == result2.gap_pos
    assert result1.gap_size == result2.gap_size
    assert result1.ctrl_states.keys() == result2.ctrl_states.keys()
    for key in result1.ctrl_states:
        assert result1.ctrl_states[key] == result2.ctrl_states[key]
    assert result1.convergence_report == result2.convergence_report


def test_simple_save(simple_system, simple_line):
    """
    Test saving during a line run.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    result = z2pack.line.run(
        system=simple_system, line=simple_line, save_file=temp_file.name
    )
    result2 = z2pack.io.load(temp_file.name, serializer=json)
    os.remove(temp_file.name)
    assert_res_equal(result, result2)


def test_weyl_save(weyl_system, weyl_line):
    """
    Test saving during a Weyl system line run.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    result = z2pack.line.run(
        system=weyl_system, line=weyl_line, save_file=temp_file.name
    )
    result2 = z2pack.io.load(temp_file.name, serializer=json)
    os.remove(temp_file.name)
    assert_res_equal(result, result2)


def test_restart(simple_system, simple_line):
    """
    Test restarting from an init_result.
    """
    result = z2pack.line.run(system=simple_system, line=simple_line)
    result2 = z2pack.line.run(
        system=simple_system, line=simple_line, init_result=result
    )
    assert_res_equal(result, result2)


def test_restart_2(weyl_system, weyl_line):
    """
    Test restarting from an init_result with changed pos_tol.
    """
    result1 = z2pack.line.run(system=weyl_system, line=weyl_line)
    result2 = z2pack.line.run(system=weyl_system, line=weyl_line, pos_tol=0.2)
    result2 = z2pack.line.run(
        system=weyl_system, line=weyl_line, init_result=result2
    )
    assert_res_equal(result1, result2)


def test_invalid_restart(simple_system, simple_line):
    """
    Test conflicting 'init_result' and 'load' option.
    """
    result = z2pack.line.run(system=simple_system, line=simple_line)
    with pytest.raises(ValueError):
        z2pack.line.run(
            system=simple_system,
            line=simple_line,
            init_result=result,
            load=True
        )


def test_file_restart(simple_system, simple_line):
    """
    Test restart from a savefile.
    """
    with tempfile.NamedTemporaryFile() as temp_file:
        result1 = z2pack.line.run(
            system=simple_system, line=simple_line, save_file=temp_file.name
        )
        result2 = z2pack.line.run(
            system=simple_system,
            line=simple_line,
            save_file=temp_file.name,
            load=True,
            serializer=json
        )
    assert_res_equal(result1, result2)


def test_load_inexisting(simple_system, simple_line):
    """
    Test that trying to load from an inexisting file raises.
    """
    with pytest.raises(IOError):
        z2pack.line.run(
            system=simple_system,
            line=simple_line,
            save_file='invalid_name',
            load_quiet=False,
            load=True,
            serializer=json
        )


def test_load_no_filename(simple_system, simple_line):
    """
    Test that trying to load without a filename given raises.
    """
    with pytest.raises(ValueError):
        z2pack.line.run(system=simple_system, line=simple_line, load=True)


def test_invalid_line(simple_system):
    """
    Test that using a line that is not connected raises.
    """
    with pytest.raises(ValueError):
        z2pack.line.run(system=simple_system, line=lambda t: [t / 2, 0, 0])


def test_invalid_path(simple_system, simple_line):
    """
    Test that trying from an invalid path raises.
    """
    with pytest.raises(ValueError):
        z2pack.line.run(
            system=simple_system,
            line=simple_line,
            save_file='invalid/path/file.json'
        )
