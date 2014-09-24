#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    21.03.2014 11:46:38 CET
# File:    z2pack.py

import python_tools.string_tools as string_tools

# for the ABINIT specialisation
import abinit.abinit_run as ar
import abinit.abinit_input_io as io

# for the tight-binding specialisation
from tight_binding.tight_binding import TbSystem
from tight_binding.tight_binding import Vectors as TbVectors

import sys
import time
import pickle
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                     GENERAL PURPOSE LIBRARY                           #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#


class Z2packSystem:
    """
    abstract Base Class for Z2Pack systems 
    method: plane
    """
    
    def __init__(self, M_handle_creator, **kwargs):
        """
        M_handle_creator: takes (string_dir, plane_pos_dir, plane_pos)
            and creates an M_handle
            --> M_handle(kx, N): creates M-matrices
        
        kwargs: passed to Z2PackPlane constructor unless overwritten
            by plane() kwargs
        """
        self._defaults = kwargs
        self._M_handle_creator = M_handle_creator
    

    def plane(self, string_dir, plane_pos_dir, plane_pos, **kwargs):
        """
        plane position: orthogonal to plane_pos_dir, at plane_pos
        strings: along string_dir
        
        kwargs: passed to Z2PackPlane constructor. Take precedence
            over kwargs from Z2PackSystem constructor.
        """
#----------------updating keyword arguments-----------------------------#
        kw_arguments = self._defaults.copy()
        kw_arguments.update(kwargs)
#----------------creating M_handle--------------------------------------#
        if(string_dir == plane_pos_dir):
            raise ValueError('strings cannot be perpendicular to the plane')
        
        return Z2packPlane(   
                                    self._M_handle_creator(string_dir, plane_pos_dir, plane_pos),
                                    **kw_arguments
                                )

class Z2packPlane:
    """
    input variables:
    Nstrings:           number of strings at the beginning (should be 
                        >= 8 for good results)
    """
    
    #----------------CONSTRUCTOR - PARSE INPUT--------------------------#
    def __init__(   self, 
                    M_handle, 
                    max_iter = 10, 
                    wcc_tol = 1e-2, 
                    gap_tol = 2e-2, 
                    Nstrings = 11, 
                    use_pickle = True, 
                    pickle_file = "res_pickle.txt", 
                    **kwargs):
        # TODO: most of those arguments belong in wcc_calc!!
        """
        constructor
        parses the input variables
        """
        self._M_handle = M_handle
        self._wcc_tol = wcc_tol
        self._gap_tol = gap_tol
        self._max_iter = max_iter
        self._use_pickle = use_pickle
        self._pickle_file = pickle_file
        self._Nstrings = Nstrings
        #----------------input checks-----------------------------------#   
        # checking Nstrings
        if(self._Nstrings < 2):
            raise ValueError("Nstrings must be at least 2")
        elif(self._Nstrings < 8):
            warnings.warn("Nstrings should usually be >= 8 for good results", UserWarning)
    
    def wcc_calc(self, verbose = True):
        """
        calculating the wcc of the system
        - automated convergence in string direction
        - automated check for distance between gap and wcc -> add string
        """
        #----------------initial output---------------------------------# # TODO: add all variables
        self._verbose = verbose
        if(self._verbose):
            print(string_tools.cbox( "starting wcc calculation\n\n" +\
                                "options:\n" +\
                                "initial # of strings: " + str(self._Nstrings) + "\n"+\
                                "use pickle: " + ("yes" if self._use_pickle else "no")
                                ) + "\n")
            
        start_time = time.time()

        #----------------initialising-----------------------------------#
        self._k_points = list(np.linspace(0, 0.5, self._Nstrings, endpoint = True))
        self._gaps = [None for i in range(self._Nstrings)]
        self._wcc_list = [[] for i in range(self._Nstrings)] 
        self._neighbour_check = [False for i in range(self._Nstrings - 1)]
        self._string_status = [False for i in range(self._Nstrings)]
        
                
        #----------------main calculation part--------------------------#
        while not (all(self._neighbour_check)):
            for i, kx in enumerate(self._k_points):
                if not(self._string_status[i]):
                    self._wcc_list[i] = self._getwcc(kx, verbose)
                    self._gaps[i] = self._gapfind(self._wcc_list[i])
                    self._string_status[i] = True
                    self._save()
                    
            self._check_neighbours()

        #----------------dump results into pickle file------------------#
        self._save()
            
            
        #----------------output to signal end of wcc calculation--------#
        end_time = time.time()
        duration = end_time - start_time
        duration_string =   str(int(np.floor(duration / 3600))) + \
                            " h " + \
                            str(int(np.floor(duration / 60)) % 60) + \
                             " min " + \
                            str(int(np.floor(duration)) % 60) + \
                            " sec"
        if(self._verbose):
            print(string_tools.cbox( "finished wcc calculation" + "\ntime: " 
                            + duration_string))
        
        #----------------return value-----------------------------------#
        return [self._k_points, self._wcc_list]
            
    #-------------------------------------------------------------------#
    #                support functions for wcc                          #
    #-------------------------------------------------------------------#

    #----------------checking distance gap-wcc--------------------------#
    def _check_neighbours(self):
        """
        checks the neighbour conditions, adds a value in k_points when
        they are not fulfilled
        - adds at most one k_point per run
        - returns Boolean: all neighbour conditions fulfilled <=> True
        """
        for i, status in enumerate(self._neighbour_check):
            if not(status):
                if(self._string_status[i] and self._string_status[i + 1]):
                    if(self._verbose):
                        print("Checking neighbouring k-points k = " + "%.4f" % self._k_points[i] + " and k = " + "%.4f" % self._k_points[i + 1] + "\n", end = "", flush = True)
                    if(self._check_single_neighbour(i, i + 1)):
                        if(self._verbose):
                            print("Condition fulfilled\n\n", end = "", flush = True)
                        self._neighbour_check[i] = True
                    else:
                        if(self._verbose):
                            print("Condition not fulfilled\n\n", end = "", flush = True)
                        # add entries to neighbour_check, k_point and string_status
                        self._neighbour_check.insert(i + 1, False)
                        self._string_status.insert(i + 1, False)
                        self._k_points.insert(i + 1, (self._k_points[i] + self._k_points[i+1]) / 2)
                        self._wcc_list.insert(i + 1, [])
                        self._gaps.insert(i + 1, None)
                        #---------check length of the variables---------#
                        assert len(self._k_points) == len(self._wcc_list)
                        assert len(self._k_points) - 1 == len(self._neighbour_check)
                        assert len(self._k_points) == len(self._string_status)
                        assert len(self._k_points) == len(self._gaps)
                        return False
                else:
                    return False
        return True
        
    
    def _check_single_neighbour(self, i, j):
        """
        checks if the gap[i] is too close to any of the WCC in 
        wcc_list[j] and vice versa
        should be used with j = i + 1
        """
        return self._check_single_direction(self._wcc_list[j], self._gaps[i])
        
    def _check_single_direction(self, wcc, gap):
        """
        checks if gap is too close to any of the elements in wcc
        """
        for wcc_val in wcc:
            if(min(abs(1 + wcc_val - gap) % 1, abs(1 - gap + wcc_val) % 1) < self._gap_tol):
                return False
        return True
        
    #----------------pickle: save and load------------------------------#
    def _save(self):
        """
        save k_points, wcc and gaps to pickle file
        only works if use_pickle = True
        """
        if(self._use_pickle):
            f = open(self._pickle_file, "wb")
            pickle.dump([self._k_points, self._wcc_list, self._gaps], f)
            f.close()
            
    def load(self):
        """
        load k_points, wcc and gaps from pickle file
        only works if use_pickle = True
        """
        if(self._use_pickle):
            f = open(self._pickle_file, "rb")
            [self._k_points, self._wcc_list, self._gaps] = pickle.load(f)
            f.close()
    
    #----------------calculating one string-----------------------------#
    def _getwcc(self, kx, verbose):
        """
        calculates WCC along a string by increasing the number of steps 
        (k-points) along the string until the WCC converge
        """
        #----------------initial output---------------------------------#
        if(self._verbose):
            print("calculating string at kx = " + "%.4f" % kx + "; N = ", end = "", flush = True)

        #----------------first two steps--------------------------------#
        N = 8
        niter = 0
        if(self._verbose):
            print(str(N), end = "", flush = True) # Output
        x, min_sv = self._trywcc(self._M_handle(kx, N), verbose)
        #----------------iteration--------------------------------------#
        while(True):
            # larger steps for small min_sv (every second step)
            if(niter % 2 == 1 and min_sv < 0.5): 
                N += 4
            else:
                N += 2
            xold = x.copy()
            if(self._verbose):
                print(", " + str(N), end = "", flush = True)    # Output
            x, min_sv = self._trywcc(self._M_handle(kx, N), verbose)
            niter += 1

            #----------------break conditions---------------------------#
            if(self._convcheck(x, xold)): # success
                if(self._verbose):
                    print(" finished!\n\n", end = "", flush = True)
                break
            if(niter > self._max_iter): # failure
                if(self._verbose):
                    print("failed to converge!\n\n", end = "", flush = True)
                break

        return sorted(x)
    
    def _trywcc(self, allM, verbose):
        """
        Calculates the WCC from the MMN matrices
        """
        Gamma = np.eye(len(allM[0]))
        min_sv = 1
        for M in allM:
            #~ [V,E,W] = la.svd(M)  # TODO: implement the second convergence criterion
            [V,E,W] = la.svd(M)
            Gamma = np.dot(np.dot(V,W).conjugate().transpose(), Gamma)
            min_sv = min(min(E), min_sv)
        # getting the wcc from the eigenvalues of gamma
        [eigs, _] = la.eig(Gamma)
        if(verbose):
            if(self._verbose):
                print(" (" + "%.3f" % min_sv + ")", end= "", flush = True)
        return [(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs], min_sv
    

        
    #----------------wcc convergence functions--------------------------#
    def _convcheck(self, x, y):
        """
        check convergence of wcc from x to y
        
        depends on: self._wcc_tol
                    roughly corresponds to the total 'movement' in WCC that
                    is tolerated between x and y
        """
        if(len(x) != len(y)):
            if(self._verbose):
                print("Warning: consecutive strings don't have the same amount of WCC")
            return False
        else:
            return self._convsum(x, y, self._wcc_tol) < 1 
    

    def _convsum(self, listA, listB, epsilon = 1e-2, N0 = 7):
        """
        helper function for _convcheck
        
        calculates the absolute value of the change in density from listA
        to listB, when each WCC corresponds to a triangle of width epsilon
        (and total density = 1)
        """
        N = N0 * int(1/(2 * epsilon))
        val = np.zeros(N)
        for x in listA:
            index = int(N*x)
            for i in range(0, N0):
                val[(index - i) % N] += 1 - (i/N0)
            for i in range(1, N0):
                val[(index + i) % N] += 1 - (i/N0)
        for x in listB:
            index = int(N*x)
            for i in range(0, N0):
                val[(index - i) % N] -= 1 - (i/N0)
            for i in range(1, N0):
                val[(index + i) % N] -= 1 - (i/N0)
        return sum(abs(val)) / N0
    #-------------------------------------------------------------------#
        
    def _gapfind(self, x):
        """
        finds the largest gap in vector x, modulo 1
        """
        x = sorted(x)
        gapsize = 0
        gappos = 0
        N = len(x)
        for i in range(0, N - 1):
            temp = x[i + 1] - x[i]
            if(temp > gapsize):
                gapsize = temp
                gappos = i
        temp = x[0] - x[-1] + 1
        if(temp > gapsize):
            gapsize = temp
            gappos = N - 1
        return (x[gappos] + gapsize / 2) % 1
    #----------------END OF SUPPORT FUNCTIONS---------------------------#        
    
    def plot(self, shift = 0):
        """
        plot WCC and largest gaps (with a shift modulo 1)
        """
        shift = shift % 1
        plt.figure()
        plt.ylim(0,1)
        plt.xlim(-0.01, 0.51)
        plt.plot(self._k_points, [(x + shift) % 1 for x in self._gaps], 'bD')
        # add plots with +/- 1 to ensure periodicity
        plt.plot(self._k_points, [(x + shift) % 1 + 1 for x in self._gaps], 'bD')
        plt.plot(self._k_points, [(x + shift) % 1 - 1 for x in self._gaps], 'bD')
        for i, kpt in enumerate(self._k_points):
            plt.plot([kpt] * len(self._wcc_list[i]), [(x + shift) % 1 for x in self._wcc_list[i]], "ro")
            # add plots with +/- 1 to ensure periodicity
            plt.plot([kpt] * len(self._wcc_list[i]), [(x + shift) % 1 + 1 for x in self._wcc_list[i]], "ro")
            plt.plot([kpt] * len(self._wcc_list[i]), [(x + shift) % 1 - 1 for x in self._wcc_list[i]], "ro")
        plt.show()
        
    
    def invariant(self):
        """
        calculate the Z2 topological invariant
        """
            
        inv = 1
        for i in range(0, len(self._wcc_list)-1):
            for j in range(0, len(self._wcc_list[0])):
                inv *= self._sgng(self._gaps[i], self._gaps[i+1], self._wcc_list[i+1][j])
        
        return 1 if inv == -1 else 0
        
    #-------------------------------------------------------------------#
    #                support functions for invariants                   #
    #-------------------------------------------------------------------#
    def _sgng(self, z, zplus, x):
        """
        calculates the invariant between two WCC strings
        """
        return np.copysign(1,np.sin(2*np.pi*(zplus - z)) + np.sin(2*np.pi*(x-zplus)) + np.sin(2*np.pi*(z-x)))
    #----------------END SUPPORT FUNCTIONS FOR INVARIANTS---------------#
    
        
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                         ABINIT SPECIALISATION                         #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
class Abinit(Z2packSystem):
    
    def __init__(   self, 
                    name,
                    common_vars_path,
                    psps_files,
                    working_folder,
                    num_occupied,
                    abinit_command = "abinit",
                    **kwargs
                    ):
        self._defaults = kwargs
        self._name = name
        self._abinit_system = ar.AbinitRun( name, 
                                            io.parse_input(common_vars_path) , 
                                            psps_files, 
                                            working_folder, 
                                            num_occupied,
                                            abinit_command = abinit_command)
        def _M_handle_creator_abinit(string_dir, plane_pos_dir, plane_pos):
            # check if kx is before or after plane_pos_dir
            if(3 - string_dir > 2 * plane_pos_dir):
                return lambda kx, N: self._abinit_system.nscf(string_dir, [plane_pos, kx], N)
            else:
                return lambda kx, N: self._abinit_system.nscf(string_dir, [kx, plane_pos], N)
        self._M_handle_creator = _M_handle_creator_abinit
        
    def scf(self, scf_vars_path, verbose = True, **kwargs):
        self._verbose = verbose
        try:
            if not(kwargs['setup_only']): 
                if(self._verbose):
                    print("starting SCF calculation for " + self._name)
            else:
                if(self._verbose):
                    print("setting up SCF calculation for " + self._name)
        except:
            if(self._verbose):
                print("starting SCF calculation for " + self._name)
        self._abinit_system.scf(io.parse_input(scf_vars_path), **kwargs)
        if(self._verbose):
            print("")
        
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                TIGHT BINDING SPECIALISATION                           #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#

class TightBinding(Z2packSystem):
    def __init__(   self,
                    tbsystem,
                    **kwargs
                    ):
        self._defaults = kwargs
        self._tbsystem = tbsystem
        def _M_handle_creator_tb(string_dir, plane_pos_dir, plane_pos):
            # check if kx is before or after plane_pos_dir
            if(3 - string_dir > 2 * plane_pos_dir):
                return lambda kx, N: self._tbsystem._getM(string_dir, [plane_pos, kx], N)
            else:
                return lambda kx, N: self._tbsystem._getM(string_dir, [kx, plane_pos], N)
        self._M_handle_creator = _M_handle_creator_tb
        
    
    
    

if __name__ == "__main__":
    print("z2pack.py")
