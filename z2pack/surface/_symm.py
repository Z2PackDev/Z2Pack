"""Utilitites to select the local symmetries of a surface from a list of all symmetries of the crystal"""

def symm_from_scf(xml_path):
    """Read symmetries from scf xml output file at xml path"""
    pass

def reduced_from_wannier(xml_path):
    """Get the basis transformation matrix from the cartesion to reduced basis"""
    pass 

def pw_symm_file(symmetries):
    """Write .sym file for use in pw2wannier90"""
    pass



def find_local(symmetries, surface):
    """
    Select those symmetries that leave all k-points on the surface invariant.
    symmetries are the 3x3 symmetry matrix in reciprocal space in the reduced basis.
    surface is a function t, s -> R^3, with the output being coordinates in the reduced basis
    """
    pass