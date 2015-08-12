#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    16.02.2015 09:27:19 CET
# File:    output.py

from __future__ import print_function

from .ptools import string_tools

import sys
import time
import numpy as np

class PrintFunctions:
    def _getwcc(func):
        def inner(self, t):
            # initial output
            _print(self, "Calculating string at t = {0:.4f}, k = {1}\n".
                format(t, string_tools.fl_to_s(self._param_fct(t, 0.))))
            #-----------------------------------------------------------#
            res = func(self, t)
            #-----------------------------------------------------------#
            if self._current['pos_tol'] is None:
                _print(self, 'no iteration\n\n')
            else:
                # check convergence flag
                if res[-1]:
                    _print(self, "finished!\n\n")
                else:
                    _print(self, 'iterator ends, failed to converge!\n\n')
            # check convergence flag
            if not res[-1]:
                self._log.log('pos check', t, string_tools.fl_to_s(self._param_fct(t, 0.)))
                    
            return res[:-1] # cut out convergence flag
        return inner

    def _trywcc(func):
        """
        decorator to print wcc after a function call (if verbose)
        """
        def inner(self, all_m):
            """
            decorated function
            """
            _print(self, '    N = ' + str(len(all_m)))
            #-----------------------------------------------------------#
            res = func(self, all_m)
            wcc = sorted(res[0])
            #-----------------------------------------------------------#
            _print(self, ' (' + '%.3f' % res[1] + ')\n        ')
            _print(self, 'WCC positions:\n        ')
            _print(self, '[')
            line_length = 0
            for val in wcc[:-1]:
                line_length += len(str(val)) + 2
                if(line_length > 60):
                    _print(self, '\n        ')
                    line_length = len(str(val)) + 2
                _print(self, str(val) + ', ')
            line_length += len(str(wcc[-1])) + 2
            if(line_length > 60):
                _print(self, '\n        ')
            _print(self, str(wcc[-1]) + ']\n')
            return res
        return inner

    def _check_neighbours(func):
        def inner(self):
            res = func(self)
            if res is None:
                _print(self, 'Skipping neighbour checks (gap check & move check).\n\n')
            return res
        return inner
    
    def _check_single_neighbour(func):
        def inner(self, i):
            _print(self, ('Checking neighbouring t-points t = {0:.4f} and ' +
                      't = {1:.4f}\n').format(self._t_points[i], self._t_points[i + 1]))
            #-----------------------------------------------------------#
            res = func(self, i)
            #-----------------------------------------------------------#
            if all(res):
                _print(self, "Condition fulfilled!\n\n")
            else:
                if not res[0]:
                    _print(self, 'Gap check not fulfilled yet.\n')
                if not res[1]:
                    _print(self, 'Move check not fulfilled yet.\n')
            return res
        return inner

    def _add_string(func):
        def inner(self, i):
            res = func(self, i)
            if res:
                _print(self, 'Added string at t = {0}\n\n'.format(self._t_points[i + 1]))
            else:
                _print(self, 'Reached minimum distance between neighbours\n\n')
            return res
        return inner

    def _wcc_calc_main(func):
        def inner(self):
            #----------------initial output-----------------------------#
            start_time = time.time()
            string = "starting wcc calculation\n\n"
            length = max(len(key) for key in self._current.keys()) + 2
            for key in sorted(self._current.keys()):
                value = str(self._current[key])
                if(len(value) > 48):
                    value = value[:45] + '...'
                string += key.ljust(length) + value + '\n'
            string = string[:-1]
            _print(self, string_tools.cbox(string) + '\n')
            #----------------computation--------------------------------#
            res = func(self)
            #----------------final output-------------------------------#
            end_time = time.time()
            duration = end_time - start_time
            duration_string = str(int(np.floor(duration / 3600))) + \
                " h " + str(int(np.floor(duration / 60)) % 60) + \
                " min " + str(int(np.floor(duration)) % 60) + " sec"
            _print(self, 
                string_tools.cbox(
                    ["finished wcc calculation" + "\ntime: " + duration_string,
                     'CONVERGENCE REPORT\n------------------\n\n' +
                    str(self._log)]) +
                '\n')
            return res
        return inner

def _print(self, string):
    if(self._current['verbose']):
        print(string, end='')
        sys.stdout.flush()

def dispatcher(func):
    return PrintFunctions.__dict__[func.__name__](func)
