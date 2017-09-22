#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fallback for the blessings library. This module does not color terminal output."""


class Terminal:
    def __getattr__(self, key):
        return lambda x: x
