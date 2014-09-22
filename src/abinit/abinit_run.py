#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    13.08.2014 12:02:54 CEST
# File:    abinit_run.py

import abinit.read_mmn as mmn
import abinit.abinit_input_io as io
import abinit.wannier90_input as wannier90_input

import os
import sys
import subprocess

#-----------------------------------------------------------------------#
#                                                                       #
#                                                                       #
#-----------------------------------------------------------------------#
class ABINIT_RUN_IMPL:
    
    def __init__(   self, 
                    name,
                    common_vars, 
                    psps_files, 
                    working_folder, 
                    num_occupied,
                    abinit_command = "abinit"
                ):
        self.name = name
        self.calling_path = os.getcwd()
        self.common_vars = common_vars
        if(working_folder[0] == "/" or working_folder[0] == "~"): # absolute
            self.working_folder = working_folder
        else: #relative
            self.working_folder = self.calling_path + '/' + working_folder
        if(isinstance(psps_files, str)):
            if(psps_files[0] == "/" or psps_files[0] == "~"): # absolute
                self.psps_files = psps_files
            else: # relative
                self.psps_files = self.calling_path + '/' + psps_files
        else:
            self.psps_files = []
            for psps_file in psps_files:
                if(psps_file[0] == "/" or psps_file[0] == "~"): # absolute
                    self.psps_files.append(psps_file)
                else: # relative
                    self.psps_files.append(self.calling_path + '/' + psps_file)
        
        self.abinit_command = abinit_command
        self.num_occupied = num_occupied
        
    def __abinit_run__  (   self, 
                            subfolder,
                            tag = "", 
                            input_wfct_path = None,
                            additional_args = {},
                            create_wannier90_input = False,
                            clean_subfolder = True,
                            setup_only = False
                        ):
        data = {}
        data.update(self.common_vars)
        data.update(additional_args)
        subfolder = self.working_folder + '/' + subfolder
        run_name = self.name + tag
        
#-------------------print input file(s) to working_folder---------------#
        if(clean_subfolder):
            try:
                subprocess.call("rm -rf " + subfolder +  "/*", shell = True) 
            except:
                pass
        
        if not(os.path.isdir(subfolder)):
            subprocess.call("mkdir " + subfolder, shell = True)
        io.produce_input(data, subfolder + "/" + run_name + ".in")
        
        if(create_wannier90_input):
            if(self.num_occupied is None):
                raise ValueError('number of occupied bands not set')
            wannier90_input.write_input(self.num_occupied, data['nband'], subfolder + '/wannier90.win')
            
#-----------------------------------------------------------------------#
#                          abinit run                                   #
#-----------------------------------------------------------------------#

#-------------------get correct runtime input---------------------------#
        abinit_runtime_input = run_name + ".in\n" + run_name + ".out\n"
        
        if(input_wfct_path is None):
            abinit_runtime_input += run_name + "_i\n"
        else:
            abinit_runtime_input += self.working_folder + "/" + input_wfct_path + "\n"
            
        abinit_runtime_input += run_name + "_o\n" + run_name + "_\n"
        
        if(isinstance(self.psps_files, str)):
            abinit_runtime_input += self.psps_files+ "\n"
        else:
            for psps_file in self.psps_files:
                abinit_runtime_input +=  psps_file + "\n"
        
        f = open(subfolder + "/" + run_name + ".files", "w")
        f.write(abinit_runtime_input)
        f.close()

#--------------------------run abinit-----------------------------------#
        if not(setup_only):
            subprocess.call(self.abinit_command + " < " + run_name + ".files" + " >& log", cwd = subfolder, shell = True)
        
#-----------------------------------------------------------------------#
#                scf run                                                #
#-----------------------------------------------------------------------#

    def scf(self, scf_args = {}, setup_only = False, **kwargs):
        scf_args.update({'prtden': 1})
        self.__abinit_run__("work_scf_" + self.name, tag = "_scf", additional_args = scf_args, setup_only = setup_only, **kwargs)
        
#-----------------------------------------------------------------------#
#                                                                       #
# string_dir in (0, 1, 2)                                               #
# string_pos = [a, b] -> shiftk [0, a, b] if string_dir = 0, [a, 0, b]  #
# if string_dir = 1, [a, b, 0] if string_dir = 2                        #
#                                                                       #
#-----------------------------------------------------------------------#
    def nscf(   self,
                string_dir, 
                string_pos, 
                string_N, 
                additional_args = {}, 
                tolwfr = 1.e-21,
                ):
                    
#----------------------prepare additional_args--------------------------#
        string_begin = list(string_pos) # avoid immutables
        string_end = list(string_pos)
        string_begin.insert(string_dir, 0)
        string_end.insert(string_dir, 1)
        #~ string_args = {"ndivk": string_N, "kptbounds": [string_begin, string_end]}
        #~ string_args.update(additional_args)
        ngkpt = [1, 1, 1]
        ngkpt[string_dir] = string_N
        string_pos.insert(string_dir,0.0)
        string_args = {'kptopt': 3}
        string_args.update({"ngkpt": ngkpt})
        string_args.update({"nshiftk": 1})
        string_args.update({"shiftk": string_pos})
        
#----------------global nscf variables----------------------------------#
        nscf_args = {}
        nscf_args.update({"iscf": -2})
        nscf_args.update({"tolwfr": tolwfr})
        nscf_args.update({"irdwfk": 1})
        nscf_args.update({"irdden": 1})
        nscf_args.update({"prtwant": 2})
        nscf_args.update({"nstep": 100})
        
        nscf_args.update(string_args)
        nscf_args.update(additional_args)

#----------------clean out working directory----------------------------#
        subfolder = "work_nscf_" + self.name
        
#----------------------call to abinit_run-------------------------------#
        self.__abinit_run__( 
                    subfolder,
                    tag = "_nscf",
                    input_wfct_path = "work_scf_" + self.name + "/" + self.name + "_scf_o", 
                    additional_args = nscf_args, 
                    create_wannier90_input = True,
                    clean_subfolder = True
                    )
#----------------------read in mmn--------------------------------------#
        M = mmn.getM(self.working_folder + '/' + subfolder + "/wannier90.mmn")
        return M

    
