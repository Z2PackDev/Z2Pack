"""pytest configuration file for Z2Pack tests."""
# pylint: disable=protected-access,redefined-outer-name,unused-argument

from collections.abc import Iterable
import json
import logging
import operator
import os

import pytest
import z2pack

from ctrl_base_tester import test_ctrl_base  # pylint: disable=unused-import

logging.getLogger("z2pack").setLevel(logging.CRITICAL)
from z2pack._utils import _get_max_move


def pytest_addoption(parser):  # pylint: disable=missing-function-docstring
    parser.addoption("--abinit", action="store_true", help="run ABINIT tests")
    parser.addoption("--vasp", action="store_true", help="run VASP tests")
    parser.addoption("--quantumespresso", action="store_true", help="run Quantum ESPRESSO tests")
    parser.addoption(
        "--no-plot-compare",
        action="store_true",
        help="disable comparing the generated plots",
    )


def pytest_configure(config):  # pylint: disable=missing-function-docstring
    # register additional marker
    config.addinivalue_line("markers", "abinit: mark tests which run with ABINIT")
    config.addinivalue_line("markers", "vasp: mark tests which run with VASP")
    config.addinivalue_line("markers", "qe: mark tests which run with Quantum ESPRESSO")


def pytest_runtest_setup(item):  # pylint: disable=missing-function-docstring
    try:
        abinit_marker = item.get_marker("abinit")
        vasp_marker = item.get_marker("vasp")
        qe_marker = item.get_marker("qe")
    except AttributeError:  # for pytest>=4
        abinit_marker = item.get_closest_marker("abinit")
        vasp_marker = item.get_closest_marker("vasp")
        qe_marker = item.get_closest_marker("qe")
    if abinit_marker is not None:
        if not item.config.getoption("--abinit"):
            pytest.skip("test runs only with ABINIT")
    if vasp_marker is not None:
        if not item.config.getoption("--vasp"):
            pytest.skip("test runs only with VASP")
    if qe_marker is not None:
        if not item.config.getoption("--quantumespresso"):
            pytest.skip("test runs only with Quantum ESPRESSO")


@pytest.fixture
def test_name(request):
    """Returns module_name.function_name for a given test"""
    return request.module.__name__ + "/" + request._parent_request._pyfuncitem.name


@pytest.fixture
def compare_data(request, test_name, scope="session"):
    """Returns a function which either saves some data to a file or (if that file exists already) compares it to pre-existing data using a given comparison function."""

    def inner(compare_fct, data, tag=None):
        full_name = test_name + (tag or "")
        val = request.config.cache.get(full_name, None)
        if val is None:
            request.config.cache.set(
                full_name,
                json.loads(json.dumps(data, default=z2pack.io._encoding.encode)),
            )
            raise ValueError("Reference data does not exist.")
        assert compare_fct(
            val, json.loads(json.dumps(data, default=z2pack.io._encoding.encode))
        )  # get rid of json-specific quirks

    return inner


@pytest.fixture
def compare_equal(compare_data):
    return lambda data, tag=None: compare_data(operator.eq, data, tag)


@pytest.fixture
def compare_wcc(compare_data):
    """Checks whether two lists of WCC (or nested lists of WCC) are almost equal, up to a periodic shift."""

    def check_wcc(wcc0, wcc1):
        """
        Check that two sets of WCC are equal.
        """
        if isinstance(wcc0[0], Iterable):
            if len(wcc0) != len(wcc1):
                return False
            return all(check_wcc(x, y) for x, y in zip(wcc0, wcc1))
        assert _get_max_move(wcc0, wcc1) < 1e-8
        return True

    return lambda data, tag=None: compare_data(check_wcc, data, tag)


@pytest.fixture
def sample():
    """
    Returns the path to the sample of the given name.
    """

    def inner(name):
        return os.path.join(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples"), name
        )

    return inner
