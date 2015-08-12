#!/usr/bin/env python
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

identifier = 'in_place_replace'

class File:
    def __init__(self, name):
        self._name = name
        with open(name, "r") as f:
            self._raw_code = f.read()
            self._code = self._raw_code.split('\n')
        self._lines = list(range(0, len(self._code)))
        self._positions = []
        # indexing all occurrences of identifier
        id_split = self._raw_code.split(identifier)
        line_num = id_split[0].count('\n')
        for line in id_split[1:]:
            beginning = line_num
            count = 0
            first = True
            found = False
            for char in line:
                if(char == '\n'):
                    line_num += 1
                if not(found): 
                    if(char == '('):
                        count += 1
                        first = False
                    elif(char == ')'):
                        count -= 1
                        if(count == 0 and not first):
                            self._positions.append((beginning, line_num))
                            found = True

    def get_pos_delete(self, line_num):
        for begin, end in self._positions:
            if(begin <= line_num and end >= line_num):
                self._positions.remove((begin, end))
                return (begin, end)

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
            return self.get_line(line_num - 1)

    def set_line(self, line_num, string):
        try:
            self._code[self._lines.index(line_num)] = string
        except ValueError:
            self.set_line(line_num - 1, string)

    def replace_before(self, line_num, expr):
        """
        replaces the first identifier(*) in the last line before or
        at line_num containing the identifier
        """
        first_line, last_line = self.get_pos_delete(line_num)

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
        self.set_line(first_line, left + repr(expr) + right)
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
        ReplaceLog.files[mod].replace_before(lineno, expr)
    else:
        ReplaceLog.files[mod] = File(mod)
        ReplaceLog.files[mod].replace_before(lineno, expr)
    return expr
