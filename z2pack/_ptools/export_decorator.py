#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.04.2016 09:51:34 CEST
# File:    export_decorator.py

import importlib

#~ test_doc = False

def export(fct):
    """Adds the decorated object to its module's __all__"""
    mod = importlib.import_module(fct.__module__)
    try:
        mod.__all__.append(fct.__name__)
    except AttributeError:
        mod.__all__ = [fct.__name__]

    #~ if test_doc:
        #~ assert fct.__doc__
    return fct
