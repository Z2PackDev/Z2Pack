#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.08.2016 23:19:46 CEST
# File:    _blessings_fallback.py

class Terminal:
    def __getattr__(self, key):
        return lambda x: x
