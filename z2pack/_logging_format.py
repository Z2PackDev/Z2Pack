#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    23.03.2016 10:05:18 CET
# File:    _logging_format.py

import sys
import logging

try:
    import blessings
# for Windows
except ImportError:
    from . import _blessings_fallback as blessings
from fsc.formatting import shorten, to_box

from ._version import __version__

def _make_title(title, delimiter, overline=False, modifier=None):
    """Creates a title by addin the appropriate over-/underline"""
    delimiter *= len(title)
    if modifier is not None:
        delimiter = modifier(delimiter)
        title = modifier(title)
    if overline:
        res = [delimiter]
    else:
        res = []
    res.extend([title, delimiter])
    return '\n'.join(res)

def _offset(string, num_offset=4):
    """Add a given offset (whitespace) to each line in the string"""
    return '\n'.join(' ' * num_offset + s for s in string.split('\n'))


class DefaultFormatter(logging.Formatter):
    """Formatter used for z2pack logs"""
    def __init__(self):
        self.term = blessings.Terminal()
        super().__init__(style='{')

    def format(self, record):
        msg = record.msg
        if hasattr(record, 'tags'):
            # Creating the Convergence Report string from its dictionary.
            if 'convergence_report' in record.tags:
                report = msg
                msg = _make_title('CONVERGENCE REPORT', '=', overline=True, modifier=self.term.bold)

                # For Surface calculations
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
                            report += '\n' + self.term.bold_green(
                                'PASSED: {0} of {1}'.format(
                                    passed, total
                                )
                            )
                        if failed:
                            report += '\n' + self.term.bold_red(
                                'FAILED: {0} of {1}'.format(
                                    failed, total
                                )
                            )
                        if missing:
                            report += '\n' + self.term.bold_yellow(
                                'MISSING: {0} of {1}'.format(
                                    missing, total
                                )
                            )
                        return _offset(title + report)
                    # line convergence objects
                    line_msg = _make_title('Line Convergence', '=')


                    for key, val in sorted(report['line'].items()):
                        line_msg += '\n\n' + make_report_entry(key, val)

                    surface_msg = _make_title('Surface Convergence', '=')
                    for key, val in sorted(report['surface'].items()):
                        surface_msg += '\n\n' + make_report_entry(key, val)
                    msg += '\n\n' + line_msg
                    msg += '\n\n' + surface_msg
                # For Line calculations
                elif 'line' in record.tags:
                    for key, val in sorted(report.items()):
                        msg += '\n\n{}: {}'.format(key, 'PASSED' if val else 'FAILED')

            if 'setup' in record.tags:
                kwargs = msg
                if 'surface' in record.tags:
                    msg = _make_title(
                        'SURFACE CALCULATION',
                        '=',
                        overline=True,
                        modifier=self.term.bold
                    )

                if 'line' in record.tags:
                    msg = _make_title(
                        'LINE CALCULATION',
                        '=',
                        overline=True,
                        modifier=self.term.bold
                    )
                msg += '\n' + 'starting at {}'.format(self.formatTime(record))
                msg += '\nrunning Z2Pack version {}\n\n'.format(__version__)

                dist = max(len(key) for key in kwargs.keys()) + 2
                format_string = '{:<' + str(dist) + '}{}'
                for key, value in sorted(kwargs.items()):
                    val_str = str(value)
                    max_width = 70 - dist
                    if len(val_str) > max_width:
                        val_str = shorten(val_str, max_width, show_number=False)
                    msg += format_string.format(key + ':', val_str)
                    msg += '\n'
                msg = msg[:-1]

            if 'timing' in record.tags:
                seconds = int(msg + 0.5) # round to the nearest second
                minutes, seconds = seconds // 60, seconds % 60
                hours, minutes = minutes // 60, minutes % 60
                days, hours = hours // 24, hours % 24
                time_str = '{}h {}m {}s'.format(hours, minutes, seconds)
                if days != 0:
                    time_str = '{}d '.format(days) + time_str
                msg = 'Calculation finished in {}'.format(time_str)

            if 'offset' in record.tags:
                msg = _offset(msg, 6)

            if 'box' in record.tags:
                msg = to_box(msg)
            else:
                msg = '{}: {}'.format(record.levelname, msg)
                if record.levelno > 25:
                    msg = self.term.bold_red(msg)

            if 'skip' in record.tags:
                msg = '\n' + msg + '\n'
            if 'skip-before' in record.tags:
                msg = '\n' + msg
            if 'skip-after' in record.tags:
                msg += '\n'



        return msg



DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
DEFAULT_HANDLER.setFormatter(DefaultFormatter())
logging.getLogger('z2pack').setLevel(logging.INFO)
logging.getLogger('z2pack').addHandler(DEFAULT_HANDLER)
