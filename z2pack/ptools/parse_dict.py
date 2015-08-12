#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    06.10.2014 13:42:33 CEST
# File:    parse_dict.py

import sys

def parse_dict(line):
    res = {}

    line = list(filter(None, line.split(",")))
    for i in range(len(line)):
        line[i] = list(filter(None, line[i].split(":")))
        if(len(line[i]) != 2):
            raise ValueError('not a valid dict entry')
        line[i][0] = line[i][0].strip()
        try:
            line[i][1] = float(line[i][1])
        except:
            try:
                line[i][1] = int(line[i][1])
            except:
                line[i][1] = line[i][1].strip()
    
    for entry in line:
        res.update({entry[0]: entry[1]})
    return res

def parse_data(data, separator = '\n'):
    data = list(filter(None, data.split(separator)))
    
    res = []
    for entry in data:
        res.append(parse_dict(entry))
        
    return res

if __name__ == "__main__":
    print("parse_dict.py")
    
