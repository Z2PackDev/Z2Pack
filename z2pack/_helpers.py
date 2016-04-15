#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.03.2016 10:21:06 CET
# File:    _helpers.py

"""Coding tools, not related to the 'physical/computation logic' of Z2Pack."""

import os
import json
import tempfile

from fsc.export import export

from . import _json_encoding

def _atomic_save(data, file_path):
    """Pickles data in an atomic way by first creating a temporary file and then moving to the file_path."""
    with tempfile.NamedTemporaryFile(
        dir=os.path.dirname(os.path.abspath(file_path)),
        delete=False,
        mode='w'
    ) as f:
        json.dump(data, f, default=_json_encoding.encode)
        os.replace(f.name, file_path)

@export
def load_result(path):
    with open(path, 'r') as f:
        return json.load(f, object_hook=_json_encoding.decode)
