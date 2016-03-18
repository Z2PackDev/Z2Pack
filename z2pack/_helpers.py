#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.03.2016 10:21:06 CET
# File:    _helpers.py

"""Coding tools, not related to the 'physical/computation logic' of Z2Pack."""

import os
import pickle
import tempfile

def _property_helper(name):
    """Checks whether an attribute of the given name exists. If it does not, the decorated function is executed, which should produce the attribute. Finally, the attribute is returned."""
    def dec(f):
        """
        The decorator itself (after a name is given).
        """
        def inner(self):
            """
            The wrapping function.
            """
            if not hasattr(self, name):
                f(self)
            return getattr(self, name)
        return inner
    return dec

def _atomic_save(data, file_path):
    """Pickles data in an atomic way by first creating a temporary file and then moving to the file_path."""
    with tempfile.NamedTemporaryFile(
        dir=os.path.dirname(os.path.abspath(file_path)),
        delete=False
    ) as f:
        pickle.dump(data, f, protocol=4)
        os.replace(f.name, file_path)
