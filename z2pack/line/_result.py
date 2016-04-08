#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

from .._result import Result
from .._ptools.export_decorator import export

@export
class LineResult(Result):
    """TODO"""
    @property
    def convergence_report(self):
        r"""
        Returns a convergence report (as a dict) for the result. The keys of the dictionary indicate the type of convergence test, and the values are booleans which are ``True`` if the test converged."""
        return {key.__name__: value for key, value in self.ctrl_convergence.items()}
