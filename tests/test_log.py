#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.07.2016 17:32:38 CEST
# File:    test_log.py

import sys
from io import StringIO

import z2pack
import logging


from em_systems import simple_system, simple_surface

def compare_lines(x, y):
    for xline, yline in zip(x.splitlines(), y.splitlines()):
        assert x == y
    return True

def test_report(capsys, compare_data, simple_system, simple_surface):
    out = StringIO()
    handler = logging.StreamHandler(stream=out)
    handler.setFormatter(z2pack._logging_format.DefaultFormatter())
    logger = logging.getLogger('z2pack')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    result = z2pack.surface.run(system=simple_system, surface=simple_surface)
    handler.flush()
    handler.close()
    logger.removeHandler(handler)
    out.seek(0)
    lines = out.read().splitlines()
    lines_notime = (
        l for l in lines if not (
            'Calculation finished' in l or
            'starting at' in l or
            'Z2Pack version' in l or
            ' at 0x' in l
        )
    )
    res = '\n'.join(lines_notime)
    compare_data(compare_lines, res)
    
