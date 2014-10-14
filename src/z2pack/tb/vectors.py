#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    25.09.2014 13:46:52 CEST
# File:    tb_vectors.py

"""
A collection of functions to easily create multiple reciprocal lattice vectors
"""

def neighbours(*args):
    """
    Adds two vectors for every axis, with +-1 in that axis (0 on 
    the other coordinates).
    
    :param args:        axes for which neighbours are to be added, either as different arguments or as a list
    :type args:         int or list(int)
    """
    res = []
    
    axes = []
    for arg in args:
        # if arg is an iterable (list, tuple,...)
        try:
            for val in arg:
                axes.append(val)
        # if arg is a single value (type safety not guaranteed)
        except TypeError:
            axes.append(arg)

    for axis in axes:
        if not(isinstance(axis, int)):
            raise TypeError('axis must be an int')
        res.append([1 if(i==axis) else 0 for i in range(3)])
        res.append([-1 if(i==axis) else 0 for i in range(3)])

    return res
    
def combine(x_vals, y_vals, z_vals):
    """
    Creates all possible combinations of the given values. ``z`` changes fastest, ``x`` slowest.
    
    :param x_vals:      Possible values for ``x``
    :type x_vals:       int or list(int)
    :param y_vals:      Possible values for ``y``
    :type y_vals:       int or list(int)
    :param z_vals:      Possible values for ``z``
    :type z_vals:       int or list(int)
    """
    res = []
    try:
        for x in x_vals:
            res.extend(combine(x, y_vals, z_vals))
    except TypeError:
        try:
            for y in y_vals:
                res.extend(combine(x_vals, y, z_vals))
        except TypeError:
            try:
                for z in z_vals:
                    res.extend(combine(x_vals, y_vals, z))
            except TypeError:
                res.append([x_vals, y_vals, z_vals])
    return res

if __name__ == "__main__":
    print("tb_vectors.py")
    
