"""Utilitites to select the local symmetries of a surface from a list of all symmetries of the crystal"""

import os
import xml.etree.ElementTree as ET
import numpy as np
import scipy.linalg as la
from fsc.export import export


def reduced_dist(k1, k2):
    """
    Calculates the distance between two vectors in reduced space.
    k1, k2: vector components given in reduced space
    """
    dist = []
    for x, y in zip(k1, k2):
        dist.append(min((x - y) % 1, (y - x) % 1))
    return dist


def to_reciprocal(real_space):
    """
    Return basis in k space given basis in x space
    real_space: list of basis vectors [x1, x2, x3]
    """
    k_space = []
    c = np.dot(real_space[0], np.cross(real_space[1], real_space[2]))
    if abs(c) < 1e-5:
        raise ValueError("Unit cell not valid")
    for i in range(3):
        k_space.append(2 * np.pi / c * np.cross(real_space[(i + 1) % 3], real_space[(i + 2) % 3]))
    return k_space

@export
def symm_from_scf(xml_path):
    """
    Read symmetries from scf xml output file at xml path
    """
    tree = ET.parse(xml_path)
    symm_xml = tree.find('output').find('symmetries').findall('symmetry')
    symmetries = []
    for symm in symm_xml:
        s = np.fromstring(symm.find('rotation').text, sep=' ')
        n = int(round(np.sqrt(len(s))))

        if np.abs(np.sqrt(len(s)) - n) > 0.001:
            raise ValueError('Symmetry matrix not square')
        symmetries.append(s.reshape((n, n)))
    return symmetries

@export
def reduced_from_wannier(xml_path):
    """
    Get the basis transformation matrix from the reduced reciprocal space to cartesian basis
    """
    real_space = []
    cell = ET.parse(xml_path).find('output').find('atomic_structure').find('cell')
    for vec in cell:
        real_space.append(np.fromstring(vec.text, sep=' '))
    return np.array(to_reciprocal(real_space)).T

@export
def pw_symm_file(symmetries, output_path):
    """
    Write .sym file for use in pw2wannier90
    symmetries: matrix of real space symmetry matrices in cartesian basis
    output_path: Path to the file to which the local symmetries are written. The filename has to "seedname".sym.
    """

    with open(output_path, 'w') as f:
        f.write(str(len(symmetries)) + '\n')
        for symm in symmetries:
            symm = np.vstack((symm, [0 for i in range(len(symm[0]))]))
            f.write('\n')
            f.write('\n'.join(map(lambda x: ' '.join(map('{:E}'.format, x)), symm)))
            f.write('\n')
        f.close()


def reduced_symm(symm, basis):
    """
    Get symmetry matrix in reciprocal space in reduced basis from symmetry matrix in real space in cartesian basis
    symm: symmetry matrix in real space in cartesian coordinates
    basis: reduced basis of real space; basis vectors as columns
    """
    symm = symm.conj()  # symmetry matrix in reciprocal space according to Sands, 1982
    BtoE = basis  # basis trafo matrix from reduced to standard basis
    EtoB = np.linalg.inv(BtoE)
    symm = EtoB.dot(symm).dot(BtoE)
    return symm

@export
def find_local(symmetries, surface, precision=3, eps=1e-5):
    """
    Select those symmetries that leave all k-points on the surface invariant.
    symmetries: 3x3 symmetry matrix in reduced real space.
    surface : function t, s -> R^3, with the output being coordinates in the reduced basis
    precision: number of random k-points for which S(k) = k is checked
    """
    local_symmetries = []
    k_points = [surface(*list(np.random.rand(2))) for i in range(precision)]

    for symm in symmetries:
        k_symm = symm.conj()
        local = True
        for kp in k_points:
            if(la.norm(reduced_dist(kp, np.dot(k_symm, kp))) > eps):
                local = False
                break
        if(local):
            local_symmetries.append(symm)
    return local_symmetries


#Tests
# xml_path = '/home/tony/Dropbox/Files/ETH/SPZ2/Z2Pack/examples/fp/Bi_qe_6.2/scf/bi.xml'
# pw_symm_file(symm_from_scf(xml_path), 'test2.sym')
# pw_symm_file(find_local(symm_from_scf(xml_path), lambda s, t: [1, s, t], reduced_from_wannier(xml_path)), 'test.sym')
# symms = symm_from_scf(xml_path)
# kk = np.array([[0, np.sqrt(3) - 1, 2], [1, -1, 2], [-1, -1, 2]]).T
# for s in symms:
#     print("------------")
#     print(kk)
#     kkp = np.dot(s, kk)
#     print(kkp)
#     print(np.linalg.solve(kk, kkp))
#     red = reduced_from_wannier(xml_path)
#     sprime = red.dot(s).dot(np.linalg.inv(red))
#     kkprime = np.dot(sprime, kk)
#     print(kkprime)
#     print(np.linalg.solve(kk, kkprime))

# def refl(n):
#     n = np.array(n)
#     n = n/la.norm(n)
#     return np.eye(3) - 2*np.outer(n, n)

# def plane(n):
#     xx = np.array([np.cross(np.eye(3)[i], n) for i in range(3)])
#     ind = np.argsort([la.norm(x) for x in xx])
#     xx = xx[ind[1:]]
#     xx = [x/la.norm(x) for x in xx]
#     return lambda s, t: s*xx[0] + t*xx[1]

# nn = [[0, 0, 1], [1, 2.3, 0]]


# symm = [refl(n) for n in nn]
# surf = [plane(n) for n in nn]

# print(reduced_dist([0.5, 0.8, 0], [1, 0.2, 1]))

