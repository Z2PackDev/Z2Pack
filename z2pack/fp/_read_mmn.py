#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    11.04.2014 13:08:23 CEST
# File:    _read_mmn.py

import re
import numpy as np

def get_m(mmn_file):
    """
    reads M-matrices from .mmn file

    args:
    ~~~~
    mmn_file:           path to .mmn file
    """
    try:
        with open(mmn_file, "r") as f:
            f.readline()

            re_int = re.compile(r'[\d]+')

            # read the first line
            num_bands, num_kpts, _ = (int(i) for i in re.findall(
                re_int,
                f.readline()
            ))

            # read the rest of the file
            lines = (line for line in f if line)

            step = num_bands * num_bands + 1
            def grouper(iterable, n):
                """Collect data into fixed-length chunks or blocks"""
                args = [iter(iterable)] * n
                return zip(*args)
            blocks = grouper(lines, step)
            M = []
            re_float = re.compile(r'[0-9.\-E]+')
            for block in blocks:
                block = iter(block)
                idx = [int(el) for el in re.findall(re_int, next(block))]
                if idx[0] % num_kpts - idx[1] != -1:
                    continue

                def to_complex(blockline):
                    k1, k2 = re.findall(re_float, blockline)
                    return float(k1) + 1j * float(k2)

                M.append(np.array([
                    [to_complex(next(block)) for _ in range(num_bands)]
                    for _ in range(num_bands)
                ]).T)

    except IOError as err:
        msg = str(err)
        msg += '. Check that the path of the .mmn file is correct (mmn_path input variable). If that is the case, an error occured during the call to the first-principles code and Wannier90. Check the corresponding log/error files.'
        raise IOError(msg) from err

    return M
