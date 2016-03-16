#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.03.2016 10:21:06 CET
# File:    _helpers.py

"""Coding tools, not related to the 'physical/computation logic' of Z2Pack."""

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
