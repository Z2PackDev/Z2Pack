"""Tests for dmn parser"""

# pylint: disable=protected-access

import pytest
import numpy as np
import z2pack


def test_read(compare_data, sample):
    compare_data(
        lambda x, y: np.equal(x, y).all(),
        z2pack.fp._read_dmn.get_dmn(sample('dmn/bi.dmn'))
    )


def test_false_path():
    with pytest.raises(IOError):
        z2pack.fp._read_dmn.get_dmn('invalid_path')
