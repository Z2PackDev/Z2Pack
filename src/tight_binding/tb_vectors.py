#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    25.09.2014 13:46:52 CEST
# File:    tb_vectors.py

import sys

"""
TbVectors module
~~~~~~~~~~~~~
Tool to easily create multiple reciprocal lattice vectors

methods: neighbour_uc, combine
"""

def neighbour_uc(axes):
    """
    adds two vectors for every axis, with +-1 in that axis (0 on 
    other coordinates)
    
    args:
    ~~~~
    axes:               list of axes for which to add neighbours
    """
    res = []
    
    # if axes is an iterable (list, tuple,...)
    try:
        for axis in axes:
            res.extend(neighbour_uc(axis))

    except:
        res.append([1 if(i==axes) else 0 for i in range(3)])
        res.append([-1 if(i==axes) else 0 for i in range(3)])
    return res
    
def combine(x_vals, y_vals, z_vals):
    """
    creates all combinations of values. z changes fastest, x slowest
    x_vals, y_vals, z_vals can be an iterable or a number
    order from the lists is preserved
    
    args:
    ~~~~
    x_vals, y_vals, z_vals:     values to combine for x,y,z
    """
    res = []
    try:
        for x in x_vals:
            res.extend(combine(x, y_vals, z_vals))
    except:
        try:
            for y in y_vals:
                res.extend(combine(x_vals, y, z_vals))
        except:
            try:
                for z in z_vals:
                    res.extend(combine(x_vals, y_vals, z))
            except:
                res.append([x_vals, y_vals, z_vals])
    return res

if __name__ == "__main__":
    print("tb_vectors.py")
    
