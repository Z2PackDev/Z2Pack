#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    27.09.2014 21:27:27 CEST
# File:    k_points.py
"""
Collection of functions for creating k-points input for different first-principles codes.
"""

import sys

def abinit(start_point, last_point, end_point, N):
    """
    For ABINIT
    """
    string = "\nkptopt -1\nndivk " + str(N - 1) + '\nkptbounds '
    for coord in start_point:
        string += str(coord).replace('e','d') + ' '
    string += '\n'
    for coord in last_point:
        string += str(coord).replace('e','d') + ' '
    string += '\n'
    return string
        
