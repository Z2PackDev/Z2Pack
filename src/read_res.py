#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    08.07.2014 20:49:23 CEST
# File:    read_res.py

import sys
import pickle
import matplotlib.pyplot as plt

def read(name):
    f = open(name, "rb")
    res = pickle.load(f)
    f.close()
    return res

if __name__ == "__main__":
    [k_points, wcc] = read("res_pickle.txt")
    print(len(k_points))
    print(len(wcc))
    for i in range(len(wcc)):
        plt.plot([k_points[i]] * len(wcc[i]), wcc[i], 'o')
    
    plt.show()
    print("read_res.py")
    
