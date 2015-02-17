#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    16.02.2015 09:27:19 CET
# File:    output.py

from __future__ import print_function

from .ptools import string_tools

import time
import numpy as np

class PrintFunctions:
    def _getwcc(func):
        def inner(self, t):
            # initial output
            self._print("Calculating string at t = {:.4f}, k = {}\n".
                format(t, string_tools.fl_to_s(self._edge_function(t))))
            #-----------------------------------------------------------#
            res = func(self, t)
            #-----------------------------------------------------------#
            if self._current['no_iter']:
                self._print('no iteration\n\n')
            else:
                # check convergence flag
                if res[-1]:
                    self._print("finished!\n\n")
                else:
                    self._print('iterator ends, failed to converge!\n\n')
            # check convergence flag
            if not res[-1]:
                self._log.log('string iteration', t, string_tools.fl_to_s(self._edge_function(t)))
                    
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
            self._print('    N = ' + str(len(all_m)))
            #-----------------------------------------------------------#
            res = func(self, all_m)
            wcc = sorted(res[0])
            #-----------------------------------------------------------#
            self._print(' (' + '%.3f' % res[1] + ')\n        ')
            self._print('WCC positions:\n        ')
            self._print('[')
            line_length = 0
            for val in wcc[:-1]:
                line_length += len(str(val)) + 2
                if(line_length > 60):
                    self._print('\n        ')
                    line_length = len(str(val)) + 2
                self._print(str(val) + ', ')
            line_length += len(str(wcc[-1])) + 2
            if(line_length > 60):
                self._print('\n        ')
            self._print(str(wcc[-1]) + ']\n')
            return res
        return inner
    
    def _check_single_neighbour(func):
        def inner(self, i):
            self._print(('Checking neighbouring t-points t = {:.4f} and ' +
                      't = {:.4f}\n').format(self._t_points[i], self._t_points[i + 1]))
            #-----------------------------------------------------------#
            res = func(self, i)
            #-----------------------------------------------------------#
            if all(res):
                self._print("Condition fulfilled!\n\n")
            else:
                if not res[0]:
                    self._print('Neighbour check not fulfilled yet.\n')
                if not res[1]:
                    self._print('Movement check not fulfilled yet.\n')
            return res
        return inner

    def _add_string(func):
        def inner(self, i):
            res = func(self, i)
            if res:
                self._print('Added string at t = {}\n\n'.format(self._t_points[i + 1]))
            else:
                self._print('Reached minimum distance between neighbours\n\n')
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
            self._print(string_tools.cbox(string) + '\n')
            #----------------computation--------------------------------#
            res = func(self)
            #----------------final output-------------------------------#
            end_time = time.time()
            duration = end_time - start_time
            duration_string = str(int(np.floor(duration / 3600))) + \
                " h " + str(int(np.floor(duration / 60)) % 60) + \
                " min " + str(int(np.floor(duration)) % 60) + " sec"
            self._print(
                string_tools.cbox(
                    ["finished wcc calculation" + "\ntime: " + duration_string,
                     'CONVERCENGE REPORT\n------------------\n\n' +
                    str(self._log)]) +
                '\n')
            return res
        return inner

def dispatcher(func):
    return PrintFunctions.__dict__[func.__name__](func)
