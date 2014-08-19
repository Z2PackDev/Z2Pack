#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    12.08.2014 16:19:26 CEST
# File:    debug.py

import string_tools

import string, re

def DEBUG(string_expr):
    variables = {}
    variables.update(globals())
    variables.update(locals())
    
    def check_for_variable(var, search_string):
        n = len(search_string)
        m = len(var)
        variable_letters = string.ascii_letters + string.digits + '_'
        indices = [occ.start() for occ in re.finditer(var, search_string)]
        if(len(indices) == 0):
            return False
        for i in indices:
            # check before 
            if(i != 0):
                if(search_string[i - 1] in variable_letters):
                    continue
            # check after
            if(i + m < n):
                if(search_string[i + m] in variable_letters):
                    continue
            return True
        return False
    
    variables = {k:v for (k,v) in variables.items() if check_for_variable(k, string_expr)}
    
    output = string_expr + " -> " 
    output += str(eval(string_expr))
    output += "\n\n"
    
    output += "variables:\n"
    vars_per_line = 4
    varnum = len(variables)
    for [i,(k,v)] in enumerate(variables.items()):
        output += k + ": " + str(v)
        if((i+ 1) % vars_per_line == 0):
            output += "\n"
        else:
            if(i != varnum - 1):
                output += ", "
    print(string_tools.cbox(output))

if __name__ == "__main__":
    x = 2
    bla = 13
    DEBUG("x+3*x**bla")

