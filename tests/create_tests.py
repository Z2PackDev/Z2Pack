#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    31.10.2014 09:53:11 CET
# File:    create_tests.py

from common import *

import os
import sys
import subprocess

subprocess.call("cp templates/* ./", shell = True)
devnull = open(os.devnull, 'w')
#~ sys.stdout = devnull
#~ sys.stderr = devnull
while(True):
    try:
        execfile('test.py')
        break
    except Exception as e:
        print(e.value)

if __name__ == "__main__":
    print("create_tests.py")
    
