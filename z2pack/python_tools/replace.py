#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    31.10.2014 13:09:41 CET
# File:    replace.py


import inspect

class ChangeLog:
    def __init__(self):
        self.files = {}

    def __del__(self):
        for val in self.files.values():
            val.writeout()

ReplaceLog = ChangeLog()

class File:
    def __init__(self, name):
        self._name = name
        with open(name, "r") as f:
            self._code = f.read().split('\n')
        self._lines = list(range(0, len(self._code)))

    def delete_line(self, line_num):
        try:
            del self._code[self._lines.index(line_num)]
            self._lines.remove(line_num)
        except ValueError:
            pass

    def get_line(self, line_num):
        try:
            return self._code[self._lines.index(line_num)]
        except ValueError:
            return ''

    def set_line(self, line_num, string):
        self._code[self._lines.index(line_num)] = string

    def replace_before(self, identifier, line_num, expr):
        """
        replaces the first identifier(*) in the last line before or
        at line_num containing the identifier
        """
        last_line = line_num
        first_line = line_num
        # catch a trailing brace
        trailing_brace = True
        check_line = ''
        for i in reversed(range(first_line)):
            tmp_line = self.get_line(i)
            if(identifier in tmp_line):
                check_line = tmp_line.rsplit(identifier)[1] + check_line
                break
            else:
                check_line = tmp_line + check_line
            if(i == 0):
                trailing_brace = False

        # check if brace closes more than once
        if(trailing_brace):
            first_zero = True
            brace_count = 0
            for char in check_line:
                if(char == '('):
                    brace_count += 1
                elif(char == ')'):
                    brace_count -= 1
                    if(brace_count == 0):
                        first_zero = False
                    if(brace_count == 0 and not first_zero):
                        trailing_brace = False
                        break

        if(trailing_brace):
            first_line -= 1
            
        
        while(True):
            if(identifier in self.get_line(first_line)):
                break
            first_line -= 1

        curr_line = ''
        for i in range(first_line, last_line + 1):
            curr_line += self.get_line(i)

        left, right = curr_line.split(identifier, 1)
        first = True
        count = 0
        for i, char in enumerate(right):
            if(char == '('):
                count += 1
                first = False
            elif(char == ')'):
                count -= 1
            if(count == 0 and not first):
                right = right[i + 1:]
                break

        self.set_line(first_line, left + str(expr) + right)
        for i in range(first_line + 1, last_line + 1):
            self.delete_line(i)

    def writeout(self):
        with open(self._name, 'w') as f:
            f.write('\n'.join(self._code))

def in_place_replace(expr):
    """in-place replacing. Must be on a single line"""
    frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
    mod = frameinfo.filename
    lineno = frameinfo.lineno - 1

    if(mod in ReplaceLog.files):
        ReplaceLog.files[mod].replace_before('in_place_replace', lineno, expr)
    else:
        ReplaceLog.files[mod] = File(mod)
        ReplaceLog.files[mod].replace_before('in_place_replace', lineno, expr)
    return expr
