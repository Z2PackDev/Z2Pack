#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.11.2014 11:36:50 CET
# File:    string_iterators.py

def wrap_iterator(func):
    def outer(*args, **kwargs):
        def inner():
            return func(*args, **kwargs)
        return inner
    return outer
    
@wrap_iterator
def constant_step(start=8, step=2):
    """default generator for the number of points in the string"""
    i = start
    while(True):
        yield(i)
        i += step
    
if __name__ == "__main__":
    print("string_iterators.py")
    
