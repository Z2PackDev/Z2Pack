#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    06.07.2014 20:20:43 CEST
# File:    string_tools.py

""" Collection of functions for formatting strings nicely """

import warnings

def cbox(   string,
            alignment = "left",
            padding = "auto",
            total_size = 70,
            centering_line = "longest"):
    """
    padding:        space on alignment side; auto -> longest/first
                    line is centered
    centering_line: longest or first -> which line to center, only
                    applies when padding is auto
    total_size:     width of the cbox (without # characters)
    alignment:      for now only left is supported
    """

    # splitting the string into lines
    lines = string.split('\n')

    # getting the values for padding
    if(padding == "auto"):
        if(centering_line != "first" and centering_line != "longest"):
            warnings.warn("centering_line: invalid argument, using 'longest'",
            UserWarning)
        if(centering_line == "first"):
            text_width = len(lines[0])
        else: # longest
            text_width = max([len(line) for line in lines])
        padding = int((total_size - text_width) / 2)

    # checking total size
    for line in lines:
        if(len(line) > total_size - padding):
            warnings.warn("strings too long, might look ugly",
            UserWarning)

    # creating the string
    endline = '+' + total_size * '-' + '+'
    cbox_str = endline + '\n'
    if(alignment == "left"):
        for line in lines:
            line_temp = '|' + padding * ' ' + line
            cbox_str += line_temp.ljust(total_size + 1) + '|\n'
        cbox_str += endline
        return cbox_str

def fl_to_s(input_list, precision=6, strip_zeros=True):
    """
    float list to string: takes a list of floats and returns a nicely
    formatted string
    """
    return '[{}]'.format(', '.join([('{:.' + str(precision) + 'f}').format(val).rstrip('0' if strip_zeros else '') for val in input_list]))
    
if __name__ == "__main__":
    print(cbox("Test:\nsuccessful"))
