"""Test the function that parses Wannier90 *.mmn files."""
# pylint: disable=protected-access

import numpy as np
import pytest

import z2pack


def test_read(compare_data, sample):
    compare_data(
        lambda x, y: np.equal(x, y).all(),
        z2pack.fp._read_mmn.get_m(sample("mmn/bi.mmn")),
    )


def test_false_path():
    with pytest.raises(IOError):
        z2pack.fp._read_mmn.get_m("invalid_path")
