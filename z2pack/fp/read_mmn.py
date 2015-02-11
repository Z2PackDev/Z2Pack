#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    11.04.2014 13:08:23 CEST
# File:    read_mmn.py


def getM(mmn_file):
    """
    reads M-matrices from .mmn file

    args:
    ~~~~
    mmn_file:           path to .mmn file
    """
    f = open(mmn_file, "r")
    f.readline()

    # read the first line
    line = [entry for entry in f.readline().split(" ") if entry]
    num_bands, num_kpts, _ = [int(l) for l in line]

    # read the rest of the file
    data = f.read()
    f.close()

    data = [entry for entry in data.split("\n") if entry]
    blocks = []
    step = num_bands * num_bands + 1
    for i in range(0, len(data), step):
        blocks.append([entry for entry in data[i:i + step] if entry])

    # extract k and k + b for each M
    idx_list = []
    for i in range(len(blocks)):
        idx_list.append([int(el) for el in
                         [entry for entry in blocks[i][0].split(" ")
                          if entry][:2]])

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
                     [entry for entry in blocks[i][j].split(" ") if entry]]
            temp.append(temp2[0] + 1j * temp2[1])

        temp2 = []
        for j in range(0, len(temp), num_bands):
            temp2.append(temp[j:j + num_bands])

        M.append([list(x) for x in zip(*temp2)])

    if not M:
        raise ValueError('The generated overlap matrix is empty. This might be due to Wannier90 computing overlaps in the wrong direction. Try increasing the initial number of k-points along the string.')

    return M
