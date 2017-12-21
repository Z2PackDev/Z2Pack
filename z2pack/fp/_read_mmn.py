"""Defines a function to parse the overlap (mmn) matrices from the Wannier90 *.mmn file."""

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
            num_bands, num_kpts, _ = (
                int(i) for i in re.findall(re_int, f.readline())
            )

            # read the rest of the file
            lines = (line for line in f if line)

            step = num_bands * num_bands + 1

            def grouper(iterable, group_size):
                """Collect data into fixed-length chunks or blocks"""
                args = [iter(iterable)] * group_size
                return zip(*args)

            blocks = grouper(lines, step)
            overlap_matrices = []
            re_float = re.compile(r'[0-9.\-E]+')
            for block in blocks:
                block = iter(block)
                idx = [int(el) for el in re.findall(re_int, next(block))]
                if idx[0] % num_kpts - idx[1] != -1:
                    continue

                def to_complex(blockline):
                    real_part, imag_part = re.findall(re_float, blockline)
                    return float(real_part) + 1j * float(imag_part)

                overlap_matrices.append(
                    np.array([[
                        to_complex(next(block)) for _ in range(num_bands)
                    ] for _ in range(num_bands)]).T
                )

    except IOError as err:
        msg = str(err)
        msg += '. Check that the path of the .mmn file is correct (mmn_path input variable). If that is the case, an error occured during the call to the first-principles code and Wannier90. Check the corresponding log/error files.'
        raise type(err)((msg)) from err
    return overlap_matrices
