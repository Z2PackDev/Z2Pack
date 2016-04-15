#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

from fsc.export import export

from .._result import Result

@export
class LineResult(Result):

    @property
    def convergence_report(self):
        r"""
        Returns a convergence report (as a dict) for the result. The keys of the dictionary indicate the type of convergence test, and the values are booleans which are ``True`` if the test converged."""
        return self.ctrl_convergence
