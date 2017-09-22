"""Test the functions that encode and decode Z2Pack objects."""
# pylint: disable=protected-access,no-member

import json

import z2pack
import pytest
import numpy as np


@pytest.mark.parametrize(
    'obj', ['foo', None, True, False, [1, 2, 3], 1, 1.2, 1 + 2j]
)
def test_consistency_exact(obj):
    """
    Test for exact equality (including type) after dumping / loading an object.
    """
    res = json.loads(
        json.dumps(obj, default=z2pack.io._encoding.encode),
        object_hook=z2pack.io._encoding.decode
    )
    assert obj == res
    assert type(obj) == type(res)  # pylint: disable=unidiomatic-typecheck


@pytest.mark.parametrize(
    'obj', [np.int32(1),
            np.float64(1.2),
            np.bool_(False),
            np.bool_(True)]
)
def test_consistency_notype(obj):
    """
    Test that dumping and loading an object gives back the same object. Does not test that the type is the same.
    """
    res = json.loads(
        json.dumps(obj, default=z2pack.io._encoding.encode),
        object_hook=z2pack.io._encoding.decode
    )
    assert obj == res


def test_invalid():
    """
    Test that trying to encode an invalid type raises.
    """

    class Bla:
        def __init__(self, x):
            self.x = x

    with pytest.raises(TypeError):
        json.dumps(Bla(2), default=z2pack.io._encoding.encode)
