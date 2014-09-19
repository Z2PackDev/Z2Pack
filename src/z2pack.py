#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    21.03.2014 11:46:38 CET
# File:    z2pack.py

import python_tools.string_tools as string_tools

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


class Z2PACK_IMPL_SYSTEM:
    
    def __init__(self, M_handle_creator, **kwargs):
        self.defaults = kwargs
        self.M_handle_creator = M_handle_creator
    

    def plane(self, string_dir, plane_pos_dir, plane_pos, **kwargs):
        """
        plane position: orthogonal to plane_pos_dir, at plane_pos
        strings: along string_dir                       
        """
#----------------updating keyword arguments-----------------------------#
        kw_arguments = self.defaults.copy()
        kw_arguments.update(kwargs)
#----------------creating M_handle--------------------------------------#
        if(string_dir == plane_pos_dir):
            raise ValueError('strings cannot be perpendicular to the plane')
        
        return Z2PACK_IMPL_PLANE(   
                                    self.M_handle_creator(string_dir, plane_pos_dir, plane_pos),
                                    **kw_arguments
                                )

class Z2PACK_IMPL_PLANE:
    """
    input variables:
    Nstrings:            number of strings at the beginning (should be 
                        >= 8 for good results)
                        TODO
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
        """
        constructor
        parses the input variables
        """
        self.__M_handle = M_handle
        self.__wcc_tol = wcc_tol
        self.__gap_tol = gap_tol
        self.__max_iter = max_iter
        self.__use_pickle = use_pickle
        self.__pickle_file = pickle_file
        self.__Nstrings = Nstrings
        #----------------input checks-----------------------------------#   
        # checking Nstrings
        if(self.__Nstrings < 2):
            raise ValueError("Nstrings must be at least 2")
        elif(self.__Nstrings < 8):
            warnings.warn("Nstrings should usually be >= 8 for good results", UserWarning)
    
    def wcc_calc(self, verbose = True):
        """
        calculating the wcc of the system
        - automated convergence in string direction
        - automated check for distance between gap and wcc -> add string
        """
        #----------------initial output---------------------------------# # TODO: add all variables
        if(verbose):
            print(string_tools.cbox( "starting wcc calculation\n\n" +\
                                "options:\n" +\
                                "initial # of strings: " + str(self.__Nstrings) + "\n"+\
                                "use pickle: " + ("yes" if self.__use_pickle else "no")
                                ) + "\n")
            
        start_time = time.time()

        #----------------initializing-----------------------------------#
        self.__k_points = list(np.linspace(0, 0.5, self.__Nstrings, endpoint = True))
        self.__gaps = [None for i in range(self.__Nstrings)]
        self.__wcc_list = [[] for i in range(self.__Nstrings)] 
        self.__neighbour_check = [False for i in range(self.__Nstrings - 1)]
        self.__string_status = [False for i in range(self.__Nstrings)]
        
                
        #----------------main calculation part--------------------------#
        while not (all(self.__neighbour_check)):
            for i, kx in enumerate(self.__k_points):
                if not(self.__string_status[i]):
                    self.__wcc_list[i] = self.__getwcc(kx, verbose)
                    self.__gaps[i] = self.__gapfind(self.__wcc_list[i])
                    self.__string_status[i] = True
                    self.__save()
                    
            self.__check_neighbours()

        #----------------dump results into pickle file------------------#
        self.__save()
            
            
        #----------------output to signal end of wcc calculation--------#
        end_time = time.time()
        duration = end_time - start_time
        duration_string =   str(int(np.floor(duration / 3600))) + \
                            " h " + \
                            str(int(np.floor(duration / 60)) % 60) + \
                             " min " + \
                            str(int(np.floor(duration)) % 60) + \
                            " sec"
        if(verbose):
            print(string_tools.cbox( "finished wcc calculation" + "\ntime: " 
                            + duration_string))
        
        #----------------return value-----------------------------------#
        return [self.__k_points, self.__wcc_list]
            
    #-------------------------------------------------------------------#
    #                support functions for wcc                          #
    #-------------------------------------------------------------------#

    #----------------checking distance gap-wcc--------------------------#
    def __check_neighbours(self):
        """
        checks the neighbour conditions, adds a value in k_points when
        they are not fulfilled
        - adds at most one k_point per run
        - returns Boolean: all neighbour conditions fulfilled <=> True
        """
        for i, status in enumerate(self.__neighbour_check):
            if not(status):
                if(self.__string_status[i] and self.__string_status[i + 1]):
                    print("Checking neighbouring k-points k = " + "%.4f" % self.__k_points[i] + " and k = " + "%.4f" % self.__k_points[i + 1] + "\n", end = "", flush = True)
                    if(self.__check_single_neighbour(i, i + 1)):
                        print("Condition fulfilled\n\n", end = "", flush = True)
                        self.__neighbour_check[i] = True
                    else:
                        print("Condition not fulfilled\n\n", end = "", flush = True)
                        # add entries to neighbour_check, k_point and string_status
                        self.__neighbour_check.insert(i + 1, False)
                        self.__string_status.insert(i + 1, False)
                        self.__k_points.insert(i + 1, (self.__k_points[i] + self.__k_points[i+1]) / 2)
                        self.__wcc_list.insert(i + 1, [])
                        self.__gaps.insert(i + 1, None)
                        #---------check length of the variables---------#
                        assert len(self.__k_points) == len(self.__wcc_list)
                        assert len(self.__k_points) - 1 == len(self.__neighbour_check)
                        assert len(self.__k_points) == len(self.__string_status)
                        assert len(self.__k_points) == len(self.__gaps)
                        return False
                else:
                    return False
        return True
        
    
    def __check_single_neighbour(self, i, j):
        """
        checks if the gap[i] is too close to any of the WCC in 
        wcc_list[j] and vice versa
        should be used with j = i + 1
        """
        return self.__check_single_direction(self.__wcc_list[j], self.__gaps[i])
        
    def __check_single_direction(self, wcc, gap):
        """
        checks if gap is too close to any of the elements in wcc
        """
        for wcc_val in wcc:
            if(min(abs(1 + wcc_val - gap) % 1, abs(1 - gap + wcc_val) % 1) < self.__gap_tol):
                return False
        return True
        
    #----------------pickle: save and load------------------------------#
    def __save(self):
        """
        save k_points, wcc and gaps to pickle file
        only works if use_pickle = True
        """
        if(self.__use_pickle):
            f = open(self.__pickle_file, "wb")
            pickle.dump([self.__k_points, self.__wcc_list, self.__gaps], f)
            f.close()
            
    def load(self):
        """
        load k_points, wcc and gaps from pickle file
        only works if use_pickle = True
        """
        if(self.__use_pickle):
            f = open(self.__pickle_file, "rb")
            [self.__k_points, self.__wcc_list, self.__gaps] = pickle.load(f)
            f.close()
    
    #----------------calculating one string-----------------------------#
    def __getwcc(self, kx, verbose):
        """
        calculates WCC along a string by increasing the number of steps 
        (k-points) along the string until the WCC converge
        """
        #----------------initial output---------------------------------#
        print("calculating string at kx = " + "%.5f" % kx + "; N = ", end = "", flush = True)

        #----------------first two steps--------------------------------#
        N = 8
        niter = 0
        print(str(N), end = "", flush = True) # Output
        x, min_sv = self.__trywcc(self.__M_handle(kx, N), verbose)
        #----------------iteration--------------------------------------#
        while(True):
            # larger steps for small min_sv (every second step)
            if(niter % 2 == 1 and min_sv < 0.5): 
                N += 4
            else:
                N += 2
            xold = x.copy()
            print(", " + str(N), end = "", flush = True)    # Output
            x, min_sv = self.__trywcc(self.__M_handle(kx, N), verbose)
            niter += 1

            #----------------break conditions---------------------------#
            if(self.__convcheck(x, xold)): # success
                print(" finished!\n\n", end = "", flush = True)
                break
            if(niter > self.__max_iter): # failure
                print("failed to converge!\n\n", end = "", flush = True)
                break

        return sorted(x)
    
    def __trywcc(self, allM, verbose):
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
            print(" (" + "%.3f" % min_sv + ")", end= "", flush = True)
        return [(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs], min_sv
    

        
    #----------------wcc convergence functions--------------------------#
    def __convcheck(self, x, y):
        """
        check convergence of wcc from x to y
        
        depends on: self.__wcc_tol
                    roughly corresponds to the total 'movement' in WCC that
                    is tolerated between x and y
        """
        if(len(x) != len(y)):
            print("Warning: consecutive strings don't have the same amount of WCC")
            return False
        else:
            return self.__convsum(x, y, self.__wcc_tol) < 1 
    

    def __convsum(self, listA, listB, epsilon = 1e-2, N0 = 7):
        """
        helper function for __convcheck
        
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
        
    def __gapfind(self, x):
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
        plt.plot(self.__k_points, [(x + shift) % 1 for x in self.__gaps], 'bD')
        # add plots with +/- 1 to ensure periodicity
        plt.plot(self.__k_points, [(x + shift) % 1 + 1 for x in self.__gaps], 'bD')
        plt.plot(self.__k_points, [(x + shift) % 1 - 1 for x in self.__gaps], 'bD')
        for i, kpt in enumerate(self.__k_points):
            plt.plot([kpt] * len(self.__wcc_list[i]), [(x + shift) % 1 for x in self.__wcc_list[i]], "ro")
            # add plots with +/- 1 to ensure periodicity
            plt.plot([kpt] * len(self.__wcc_list[i]), [(x + shift) % 1 + 1 for x in self.__wcc_list[i]], "ro")
            plt.plot([kpt] * len(self.__wcc_list[i]), [(x + shift) % 1 - 1 for x in self.__wcc_list[i]], "ro")
        plt.show()
        
    
    def invariant(self):
        """
        calculate the Z2 topological invariant
        """
            
        inv = 1
        for i in range(0, len(self.__wcc_list)-1):
            for j in range(0, len(self.__wcc_list[0])):
                inv *= self.__sgng(self.__gaps[i], self.__gaps[i+1], self.__wcc_list[i+1][j])
        
        return 1 if inv == -1 else 0
        
    #-------------------------------------------------------------------#
    #                support functions for invariants                   #
    #-------------------------------------------------------------------#
    def __sgng(self, z, zplus, x):
        """
        calculates the invariant between two WCC strings
        """
        return np.copysign(1,np.sin(2*np.pi*(zplus - z)) + np.sin(2*np.pi*(x-zplus)) + np.sin(2*np.pi*(z-x)))
    #----------------END SUPPORT FUNCTIONS FOR INVARIANTS---------------#
    
    

#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                         ABINIT SPECIALIZATION                         #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#


import abinit_run as ar
import abinit_input_io as io

class abinit(Z2PACK_IMPL_SYSTEM):
    
    def __init__(   self, 
                    name,
                    common_vars_path,
                    psps_files,
                    working_folder,
                    num_occupied,
                    abinit_command = "abinit",
                    **kwargs
                    ):
        self.defaults = kwargs
        self.__name = name
        self.__abinit_system = ar.ABINIT_RUN_IMPL(  name, 
                                                    io.parse_input(common_vars_path) , 
                                                    psps_files, 
                                                    working_folder, 
                                                    num_occupied,
                                                    abinit_command = abinit_command)
        def __M_handle_creator_abinit(string_dir, plane_pos_dir, plane_pos):
            if(3 - string_dir > 2 * plane_pos_dir):
                return lambda kx, N: self.__abinit_system.nscf(string_dir, [kx, plane_pos], N)
            else:
                return lambda kx, N: self.__abinit_system.nscf(string_dir, [plane_pos, kx], N)
        self.M_handle_creator = __M_handle_creator_abinit
        
    def scf(self, scf_vars_path, **kwargs):
        print("starting SCF calculation for " + self.__name)
        self.__abinit_system.scf(io.parse_input(scf_vars_path), **kwargs)
        print("")
        
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                TIGHT BINDING SPECIALIZATION                           #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#

class tight_binding(Z2PACK_IMPL_SYSTEM):
    pass
    

if __name__ == "__main__":
    print("z2pack.py")
