#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    09.02.2015 18:05:49 CET
# File:    csv_parser.py

def to_number(string):
    try:
        return int(string)
    except ValueError:
        return float(string)

def read_file(file_name, separator=',', ignore=[]):
    """
    splits input lines into blocks where the length does not change
    """
    with open(file_name, 'r') as f:
        data = f.read().split('\n')

    # filter out ignore
    data = [data[i] for i in range(len(data)) if i not in ignore]

    for i in range(len(data)):
        data[i] = [x for x in data[i].split(separator) if x]
        data[i] = [y for y in [x.strip() for x in data[i]] if y]
        data[i] = [to_number(x) for x in data[i]]
    
    res = []
    tmp = []
    tmp_length = len(data[0])

    for line in data:
        if line:
            if len(line) == tmp_length:
                tmp.append(line)
            else:
                res.append(tmp)
                tmp_length = len(line)
                tmp = []
                tmp.append(line)
    res.append(tmp)
    res = list(filter(None, res))
    return res
