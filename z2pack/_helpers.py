#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.03.2016 10:21:06 CET
# File:    _helpers.py

"""Coding tools, not related to the 'physical/computation logic' of Z2Pack."""

import os
#~ import msgpack
import pickle
import tempfile

from fsc.export import export

from . import _encoding

def _atomic_save(data, file_path):
    """Pickles data in an atomic way by first creating a temporary file and then moving to the file_path."""
    with tempfile.NamedTemporaryFile(
        dir=os.path.dirname(os.path.abspath(file_path)),
        delete=False,
        mode='wb'
    ) as f:
        #~ msgpack.dump(data, f, default=_encoding.encode)
        pickle.dump(data, f)
        os.replace(f.name, file_path)

@export
def load_result(path):
    with open(path, 'rb') as f:
        #~ return msgpack.load(f, object_hook=_encoding.decode)
        return pickle.load(f)
