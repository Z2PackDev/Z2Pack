#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.11.2014 11:36:50 CET
# File:    string_iterators.py


class ConstantStep:
    def __init__(self, start=8, step=2):
        self._n = start
        self._step = step

    def __iter__(self):
        return self

    def next(self):
        n = self._n
        self._n += self._step
        return n

    def __str__(self):
        return 'start: {0}, step: {1}'.format(self._n, self._step)

if __name__ == "__main__":
    print("string_iterators.py")
    
