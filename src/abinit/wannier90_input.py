#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    13.08.2014 12:27:41 CEST
# File:    wannier90_input.py

import sys

def write_input(num_wann, num_bands, file_path, spinors = True):
    input_string =  "num_wann " + str(num_wann) + "\n" +\
                    "num_bands " + str(num_wann) + "\n"
                    
    if(spinors):
        input_string += "spinors : true\n"
    else:
        input_string += "spinors : false\n"
        
    input_string += "num_iter 0\nshell_list 1\n"
    input_string += "exclude_bands " + str(num_wann + 1) + " - " + str(num_bands)
    
    f = open(file_path, 'w')
    f.write(input_string)
    f.close()
