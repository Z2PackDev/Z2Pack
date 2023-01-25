"""Test logging output."""
# pylint: disable=unused-import,redefined-outer-name

from contextlib import contextmanager
from io import StringIO  # pylint: disable=no-name-in-module
import logging

import z2pack

from hm_systems import simple_line, simple_surface, simple_system, simple_volume

IGNORE_LINES = ["Calculation finished", "starting at", "Z2Pack version", " at 0x"]


def compare_lines(x, y):
    """
    Compare two outputs, skipping the IGNORE_LINES.
    """
    for i, (xline, yline) in enumerate(zip(x.splitlines(), y.splitlines())):
        if any((part in xline) and (part in yline) for part in IGNORE_LINES):
            continue
        assert xline == yline, f"Line {i} does not match:\n\n{xline}\n!=\n{yline}"
    return True


@contextmanager
def capture_logging_output(compare_data):
    """
    Context manager that captures the logging output, and compares it to the previously obtained value.
    """
    out = StringIO()
    handler = logging.StreamHandler(stream=out)
    handler.setFormatter(
        z2pack._logging_format.DefaultFormatter()  # pylint: disable=protected-access
    )
    logger = logging.getLogger("z2pack")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    yield
    handler.flush()
    logger.removeHandler(handler)
    out.seek(0)
    res = out.read()
    compare_data(compare_lines, res)


def test_volume_report(compare_data, simple_system, simple_volume):
    with capture_logging_output(compare_data):
        z2pack.volume.run(system=simple_system, volume=simple_volume)


def test_surface_report(compare_data, simple_system, simple_surface):
    with capture_logging_output(compare_data):
        z2pack.surface.run(system=simple_system, surface=simple_surface)


def test_line_report(compare_data, simple_system, simple_line):
    with capture_logging_output(compare_data):
        z2pack.line.run(system=simple_system, line=simple_line)
