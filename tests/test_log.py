#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from io import StringIO
from contextlib import contextmanager

import z2pack
import logging

from hm_systems import simple_system, simple_surface, simple_line

IGNORE_LINES = [
    'Calculation finished', 'starting at', 'Z2Pack version', ' at 0x'
]


def compare_lines(x, y):
    for xline, yline in zip(x.splitlines(), y.splitlines()):
        if any((part in xline) and (part in yline) for part in IGNORE_LINES):
            continue
        assert xline == yline
    return True


@contextmanager
def CaptureLoggingOutput(compare_data):
    out = StringIO()
    handler = logging.StreamHandler(stream=out)
    handler.setFormatter(z2pack._logging_format.DefaultFormatter())
    logger = logging.getLogger('z2pack')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    yield
    handler.flush()
    logger.removeHandler(handler)
    out.seek(0)
    res = out.read()
    compare_data(compare_lines, res)


def test_surface_report(compare_data, simple_system, simple_surface):
    with CaptureLoggingOutput(compare_data):
        result = z2pack.surface.run(
            system=simple_system, surface=simple_surface
        )


def test_line_report(compare_data, simple_system, simple_line):
    with CaptureLoggingOutput(compare_data):
        result = z2pack.line.run(system=simple_system, line=simple_line)
