"""Tests for dmn parser"""

# pylint: disable=protected-access

import pytest
import z2pack
import numpy as np


def test_read(compare_data):
    compare_data(
        lambda x, y: np.equal(x, y).all(),
        z2pack.fp._read_dmn.get_dmn('samples/dmn/bi.dmn')
    )


def test_false_path():
    with pytest.raises(IOError):
        z2pack.fp._read_dmn.get_dmn('invalid_path')
