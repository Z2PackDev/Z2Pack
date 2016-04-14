#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

from fsc.export import export

from .._result import Result

@export
class SurfaceResult(Result):
    
    @property
    def convergence_report(self):
        r"""
        Returns a convergence report (as a string) for the result. This report shows whether the convergence options used for calculating this result were satisfied or not.
        """
        report = dict()
        #~ def section_heading(name):
            #~ return name + '\n' + '=' * len(name) + '\n\n'
        
        #~ def ctrl_heading(ctrl):
            #~ return ctrl.__name__ + '\n' + '-' * len(ctrl.__name__) + '\n\n'
        
        line_report = dict()
        line_c_ctrl = set()
        for line in self.lines:
            line_c_ctrl.update(line.ctrl_convergence.keys())
        for c_ctrl in sorted(list(line_c_ctrl), key=lambda x: x.__name__):
            ctrl_report = dict()
            passed_t = []
            failed_t = []
            missing_t = []
            for line in self.lines:
                try:
                    if line.ctrl_convergence[c_ctrl]:
                        passed_t.append(line.t)
                    else:
                        failed_t.append(line.t)
                except KeyError:
                    missing_t.append(line.t)
            ctrl_report['PASSED'] = passed_t
            ctrl_report['FAILED'] = failed_t
            ctrl_report['MISSING'] = missing_t
            line_report[c_ctrl.__name__] = ctrl_report
        report['line'] = line_report

        surface_report = dict()
        for c_ctrl, converged in sorted(self.ctrl_convergence.items(), key=lambda x: x[0].__name__):
            if converged is None:
                ctrl_report = None
            else:
                ctrl_report = dict()
                ctrl_report['PASSED'] = []
                ctrl_report['FAILED'] = []
                for t_pair, conv in zip(zip(self.t[:-1], self.t[1:]), converged):
                    if conv:
                        ctrl_report['PASSED'].append(t_pair)
                    else:
                        ctrl_report['FAILED'].append(t_pair)
            surface_report[c_ctrl.__name__] = ctrl_report
        report['surface'] = surface_report

        return report
