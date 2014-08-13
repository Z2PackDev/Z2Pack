#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    04.07.2014 14:38:23 CEST
# File:    wcc_convergence.py

import sys
import time
import numpy as np

if __name__ == "__main__":
    start = time.clock()
    epsilon = 2e-3
    N0 = 5
    listA = [0.01, 0.55, 0.6, 0.61, 0.99]
    listB = [0.01, 0.55, 0.6, 0.61, 0.01]
    
    def __convsum(listA, listB, epsilon = epsilon, N0 = 5):
        N = N0 * int(1/(2*epsilon))
        val = np.zeros(N)
        for x in listA:
            index = int(N*x)
            for i in range(0, N0):
                val[(index - i) % N] += 1 - (i/N0)
            for i in range(1, N0):\
                val[(index + i) % N] += 1 - (i/N0)
        for x in listB:
            index = int(N*x)
            for i in range(0, N0):
                val[(index - i) % N] -= 1 - (i/N0)
            for i in range(1, N0):\
                val[(index + i) % N] -= 1 - (i/N0)
        return sum(abs(val)) / N0
                

    
    
    print(__convsum(listA, listB))
    stop = time.clock()
    print(stop - start)
    print("test.py")
    

