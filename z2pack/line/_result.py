#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

from .._result import Result

class LineResult(Result):
    """TODO"""
    @property
    def convergence_report(self):
        r"""
        Returns a convergence report (as a string) for the result. This report shows whether the convergence options used for calculating this result were satisfied or not.
        """
        report = []
        for key, value in sorted(self.ctrl_convergence.items(), key=lambda x: x[0].__name__):
            report.append(
                '{:<20}{}'.format(
                    key.__name__ + ': ',
                    ('Passed' if value else 'Failed')
                )
            )
        return '\n'.join(report)
