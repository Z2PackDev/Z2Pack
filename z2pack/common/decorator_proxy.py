#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    23.10.2015 14:27:33 CEST
# File:    decorator_proxy.py

try:
    import decorator
except ImportError:
    from . import decorator_stub as decorator
