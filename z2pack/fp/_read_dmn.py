"""Parser for .dmn matrices (output from pw2wannier90)"""

import numpy as np
import re


def make_blocks(lines):
    blocks = []
    b = []
    for line in lines:
        if not line.strip() and b != []:
            blocks.append(b)
            b = []
        else:
            b.append(line)
            if(line == lines[-1]):
                blocks.append(b)
    return blocks


def read_integer_block(block):
    re_int = re.compile(r'[\d]+')
    ret = []
    for line in block:
        for i in re.findall(re_int, line):
            ret.append(int(i))
    return ret


def read_dmn_matrix(block, num_bands):
    """
    read individual dmn matrix to numpy array
    """
    def to_complex(blockline):
        re_float = re.compile(r'[0-9.\-\+E]+')
        real_part, imag_part = re.findall(re_float, blockline)
        return float(real_part) + 1j * float(imag_part)
    ret = []
    for line in block:
        ret.append(to_complex(line))
    return np.reshape(np.array(ret), (num_bands, num_bands)).T


def get_dmn(dmn_path):
    """
    Returns the dmn matrices as a nested list:
    [for each k point (not only irred. ones): [for each symmetry: dmn_matrix]]
    """
    try:
        with open(dmn_path, "r") as f:
            f.readline()  # remove first line (comment)
            dmn_matrices = []
            block_counter = 0
            lines = [line for line in f]
            blocks = make_blocks(lines)

            # Read line with parameters
            num_bands, nsymmetry, nkptirr, num_kpts = read_integer_block(blocks[block_counter])
            block_counter += 1

            # read num_kps block
            kpts_mapping = read_integer_block(blocks[block_counter])
            block_counter += 1

            # nkptirr block can be skipped
            block_counter += 1

            # nsymmetry data (nkptirr blocks) can be skipped
            block_counter += nkptirr

            # D matrices (nkptirr * nsymmetry blocks) can be skipped
            block_counter += nkptirr * nsymmetry

            # read d matrices (nkptirr * nsymmetry) blocks of data
            for k in range(num_kpts):
                dmn_k = []
                k_irred = kpts_mapping[k] - 1
                for isym in np.arange(nsymmetry) + block_counter + nsymmetry * k_irred:  # iterate over blocks belonging to the curent k point
                    dmn_k.append(read_dmn_matrix(blocks[isym], num_bands))
                dmn_matrices.append(dmn_k)

    except IOError as err:
        msg = str(err)
        msg += '. Check that the path of the .dmn file is correct (dmn_path input variable). If that is the case, an error occured during the call to the first-principles code and Wannier90. Check the corresponding log/error files.'
        raise type(err)((msg)) from err

    return dmn_matrices
