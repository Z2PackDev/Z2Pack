#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    04.06.2015 14:26:21 CEST
# File:    helpers.py

"""
Helper functions for creating tight-binding models.
"""

def matrix_to_hoppings(mat, idx_offset=0, G=[0, 0, 0], multiplier=1.):
    """
    Turns a matrix into a series of hopping terms.
    """
    hop = []
    for i, row in enumerate(mat):
        for j, x in enumerate(row):
            hop.append([i + idx_offset, j + idx_offset, np.array(G, dtype=int), multiplier * x])
    return hop

    
