#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pytest
import importlib

import fsc.export


# This should never appear in any serious code ;)
# To out-manoeuver pickle's caching, and force re-loading z2pack
def test_all_doc():
    old_name = 'z2pack'
    new_name = 'hoopy_z2pack'
    for key in list(sys.modules.keys()):
        # move previous z2pack to hoopy_z2pack
        if key.startswith(old_name):
            new_key = key.replace(old_name, new_name)
            sys.modules[new_key] = sys.modules[key]
            del sys.modules[key]
    fsc.export.test_doc()
    try:
        import z2pack
    finally:
        # reset to the previous z2pack -- just doing import breaks pickle
        for key in list(sys.modules.keys()):
            if key.startswith(old_name):
                del sys.modules[key]
        for key in list(sys.modules.keys()):
            if key.startswith(new_name):
                new_key = key.replace(new_name, old_name)
                sys.modules[new_key] = sys.modules[key]
                del sys.modules[key]
