#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.05.2014 08:33:00 CEST
# File:    progressbar.py

import sys
import time

def progressbar(val, maxval, width = 50):
    n = int(val * width / float(maxval) + 1e-8)
    sys.stdout.write("\r[" + n * "*" + (width - n) * "-" + "]")
    sys.stdout.flush()

if __name__ == "__main__":
    test_length = 33
    test_step = 0.1
    for i in range(test_length):
        progressbar(i, test_length - 1)
        time.sleep(0.1)
    print("progressbar.py")
    
