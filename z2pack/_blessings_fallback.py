#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Terminal:
    def __getattr__(self, key):
        return lambda x: x
