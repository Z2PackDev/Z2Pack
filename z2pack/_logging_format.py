#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    23.03.2016 10:05:18 CET
# File:    _logging_format.py

import logging
from .ptools.string_tools import cbox

def _make_title(title, delimiter, overline=False):
    delimiter *= len(title)
    if overline:
        res = [delimiter]
    else:
        res = []
    res.extend([title, delimiter])
    return '\n'.join(res)

def _offset(string, num_offset=4):
    return '\n'.join(' ' * num_offset + s for s in string.split('\n'))

    
class DefaultFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(style='{')

    def format(self, record):
        msg = record.msg
        if hasattr(record, 'tags'):
            # Creating the Convergence Report string from its dictionary.
            if 'convergence_report' in record.tags:
                report = msg
                msg = _make_title('CONVERGENCE REPORT', '=', overline=True)
                
                if 'surface' in record.tags:
                    def make_report_entry(key, val):
                        title = _make_title(key, '-')
                        if val is None:
                            return _offset(title + '\nFAILED: Convergence check has not run!')
                        passed = len(val['PASSED'])
                        failed = len(val['FAILED'])
                        try: 
                            missing = len(val['MISSING'])
                        except KeyError:
                            missing = 0
                        total = sum([passed, failed, missing])
                        report = ''
                        if passed:
                            report += '\n' + 'PASSED: {} of {}'.format(passed, total)
                        if failed:
                            report += '\n' + 'FAILED: {} of {}'.format(failed, total)
                        if missing:
                            report += '\n' + 'MISSING: {} of {}'.format(missing, total)
                        return _offset(title + report)
                    # line convergence objects
                    line_msg = _make_title('Line Convergence', '=')

                        
                    for key, val in report['line'].items():
                        line_msg += '\n\n' + make_report_entry(key, val)

                    surface_msg = _make_title('Surface Convergence', '=')
                    for key, val in report['surface'].items():
                        surface_msg += '\n\n' + make_report_entry(key, val)
                    msg += '\n\n' + line_msg
                    msg += '\n\n' + surface_msg
                elif 'line' in record.tags:
                    for key, val in report.items():
                        msg += '\n\n{}: {}'.format(key, 'PASSED' if val else 'FAILED')

            if 'setup' in record.tags:
                if 'surface' in record.tags:
                    pass
                if 'line' in record.tags:
                    pass

            if 'box' in record.tags:
                msg = '\n' + cbox(msg) + '\n'

            else:
                msg = '{}: {}'.format(record.levelname, msg)

            if 'offset' in record.tags:
                msg = _offset(msg, 6)

        return msg

    

default_handler = logging.StreamHandler()
default_handler.setFormatter(DefaultFormatter())
logging.getLogger('z2pack').setLevel(logging.INFO)
logging.getLogger('z2pack').addHandler(default_handler)
