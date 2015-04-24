#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    31.10.2014 09:53:11 CET
# File:    create_tests.py

from common import *
import sys

import os
import shutil
import subprocess


if __name__ == "__main__":
    subprocess.call("cp templates/* ./", shell = True)
    execfile('test.py', globals(), locals())
    
