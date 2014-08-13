#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    06.05.2014 16:14:16 CEST
# File:    input_io.py

import sys
import numpy as np
    
def parse_input(name):
    in_file = open(name, "r")
    text = in_file.read()
    in_file.close()
    text = text.replace("\t", " ")
    text = text.split("\n")
    
    # delete comments
    for i in range(len(text)):
        hashtag = text[i].find("#")
        if(hashtag != -1):
            text[i] = text[i][:hashtag]
        
        # split by whitespaces
        text[i] = list(filter(None, text[i].split(" ")))
        
    
    # delete empty rows
    text = list(filter(None, text))
        
    text_formatted = []
    var_indices = []
    num_incr = 0
    # move name to a separate line
    for i, line in enumerate(text):
        try:
            float(line[0].replace("d","e"))
            text_formatted.append(line)
        except:
            text_formatted.append(line[0])
            var_indices.append(i + num_incr)
            if(len(line) > 1):
                text_formatted.append(line[1:])
                num_incr += 1
    var_indices.append(len(text_formatted)) # ending flag
    
    
    data = {}
    def to_number(x):
    # expand x*y 
    # the expression '*x' gets put into a tuple ('*', x)
    # 'y*x' gets expanded to a list containing y elements x
        index = x.find('*')
        if(index != -1):
            if(index == 0):
                return ('*', to_number(x[1:]))
            else:
                return [to_number(x[index + 1:])] * to_number(x[:index])
    # regular numbers
        else:
            y = x.replace('d', 'e')
            try:
                return int(y)
            except:
                try:
                    return float(y)
                except:
                    return x
                
    def get_value(x):
        if(len(x) == 1):
            return to_number(x[0])
        else:
            return [to_number(val) for val in x]
            
    for i, index in enumerate(var_indices[:-1]):
        if(var_indices[i + 1] - var_indices[i] == 2):
            data.update({text_formatted[index]: get_value(text_formatted[index + 1])})
        else:
            res = [get_value(text_formatted[j]) for j in range(index + 1, var_indices[i + 1])]
            data.update({text_formatted[index]: res})
    return data
    
def produce_input(data, name):
    stream = open(name, "w")
    
    keys = list(data.keys())
    idx = np.argsort(keys)
    
    def print_tool(l, stream):
        if not isinstance(l, list):
            print_tool_list([l], stream)
        else:
            print_tool_list(l, stream)
            
    def print_tool_list(l, stream):
        if isinstance(l, tuple):
            for x in l:
                stream.write(str(x))
        elif not isinstance(l, list):
            stream.write(str(l) + " ")
        else:
            for x in l:
                print_tool_list(x, stream) 
            stream.write('\n')
    
    for i in range(len(keys)):
        stream.write(str(keys[idx[i]]) + "\n")
        print_tool(data[keys[idx[i]]], stream)
        stream.write('\n')
    
    stream.close()
            

