#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    11.04.2014 13:08:23 CEST
# File:    _read_mmn.py

import re

def getM(mmn_file):
    """
    reads M-matrices from .mmn file

    args:
    ~~~~
    mmn_file:           path to .mmn file
    """
    try:
        with open(mmn_file, "r") as f:
            f.readline()

            # read the first line
            line = re.findall('[\d]+', f.readline())
            num_bands, num_kpts, _ = [int(l) for l in line]

            # read the rest of the file
            data = f.read()
    except IOError as e:
        msg = str(e)
        msg += '. Check that the path of the .mmn file is correct (mmn_path input variable). If that is the case, an error occured during the call to the first-principles code and Wannier90. Check the corresponding log/error files.'
        raise IOError(msg)

    data = [entry for entry in data.split("\n") if entry]
    blocks = []
    step = num_bands * num_bands + 1
    for i in range(0, len(data), step):
        blocks.append([entry for entry in data[i:i + step] if entry])

    # extract k and k + b for each M
    idx_list = []
    for i in range(len(blocks)):
        idx_list.append([int(el) for el in
                         re.findall('[\d]+', blocks[i][0])[:2]])

    # extract M
    M = []
    for i in range(len(blocks)):
        # check if element has to be in the string
        if(idx_list[i][0] % num_kpts - idx_list[i][1] != -1):
            continue
        # end check
        temp = []
        for j in range(1, len(blocks[i])):
            temp2 = [float(k) for k in
                     re.findall('[0-9.\-E]+', blocks[i][j])]
            temp.append(temp2[0] + 1j * temp2[1])

        temp2 = []
        for j in range(0, len(temp), num_bands):
            temp2.append(temp[j:j + num_bands])

        M.append([list(x) for x in zip(*temp2)])

    return M
