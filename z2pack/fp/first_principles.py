#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    26.09.2014 22:44:18 CEST
# File:    first_principles.py

from . import kpts
from .. import System as _Z2PackSystem
from . import read_mmn as mmn

import os
import re
import sys
import copy
import shutil
import platform
import subprocess


class System(_Z2PackSystem):
    r"""
    A subclass of :class:`z2pack.System` designed to work with various first - 
    principles codes.

    :param input_files:             Path(s) of the input file(s)
    :type input_files:              str or list

    :param k_points_fct:            Fct that creates a ``str`` specifying 
        the k-points (in the language of the first-principles code used), 
        given a ``starting_point``, ``last_point``, ``end point`` and number 
        of k-points ``N``. Can also be a ``list`` of functions if k-points 
        need to be written to more than one file.

    :param k_points_path:           Name of the file where the k-points 
        ``str`` belongs. Will append to a file if it matches one of the 
        ``file_names``, and create a separate file else. 
        If ``k_points_fct`` is a ``list``, ``k_points_path`` should also be 
        a list, specifying the path for each of the functions.
    :type k_points_path:            str or list of str

    :param working_folder:          Folder where the created input files go
    :type working_folder:           str

    :param command:                 Command to execute the first principles 
        code
    :type command:                  str

    :param executable:              Sets the executable executing the command
    :type executable:               str

    :param file_names:              Name(s) the input file(s) should get 
        in the ``working_folder``. Default behaviour is taking the filenames 
        from the input files.
    :type file_names:               str or list

    :param mmn_path:                Path to the ``.mmn`` output file of 
        ``Wannier90``
    :type mmn_path:                 str

    :param clean_subfolder:         Toggles deleting the content of 
        ``working_folder`` before starting a new calculation.
    :type clean_subfolder:          bool

    :param kwargs:                  Are passed to the :class:`.Surface` 
        constructor via :meth:`.plane`. More recent arguments take precendence.

    .. note:: ``input_files`` and ``working_folder`` can be absolute or relative 
        paths, the rest is relative ``to working_folder``
    """
    def __init__(self,
                 input_files,
                 k_points_fct,
                 k_points_path,
                 working_folder,
                 command,
                 executable=None,
                 file_names='copy',
                 mmn_path='wannier90.mmn',
                 clean_working_folder=True,
                 **kwargs):

        self._system = _FirstPrinciplesSystem(input_files,
                                              k_points_fct,
                                              k_points_path,
                                              working_folder,
                                              command,
                                              executable,
                                              file_names,
                                              mmn_path,
                                              clean_working_folder)
        self._defaults = kwargs

        def _m_handle_creator_first_principles(edge_function, string_vec):
            return lambda kx, N: self._system._run(edge_function(kx), string_vec, N)

        self._m_handle_creator = _m_handle_creator_first_principles


class _FirstPrinciplesSystem:

    def __init__(self,
                 input_files,
                 k_points_fct,
                 k_points_path,
                 working_folder,
                 command,
                 executable=None,
                 file_names='copy',
                 mmn_path='wannier90.mmn',
                 clean_subfolder=True):
        """
        args:
        ~~~~
        input_files:            path(s) of the input file(s) (str or list)
        k_points_fct:           fct that creates k_point string, given
                                starting point, last_point, end point, N
        k_points_path:          name of the file where k_points belong
                                will append to a file if it matches one
                                of file_names, create a separate file
                                else
        working_folder:         folder where the created input files go
        command:                command to execute the first principles
                                code

        kwargs:
        ~~~~~~
        file_names:             name(s) the input file(s) should get
                                put 'copy' -> same as input_files
        mmn_path:               path of the .mmn file (default:
                                wannier90.mmn)
        clean_subfolder:        toggles deleting content of
                                working_folder before starting a new
                                calculation

        file paths:
        ~~~~~~~~~~
        input_files and working_folder can be absolute or relative
        paths, the rest is relative to working_folder
        """
        # catch Windows
        if(re.match('Windows', platform.platform(), re.IGNORECASE)):
            self._sep = '\\'
            self._is_windows = True
        else:
            self._sep = '/'
            self._is_windows = False

        # convert to lists (input_files)
        if not isinstance(input_files, str):
            self._input_files = list(input_files)
        else:
            self._input_files = [input_files]

        # copy to file_names and split off the name
        if(file_names == 'copy'):
            self._file_names = copy.copy(self._input_files)
            for i in range(len(self._input_files)):
                self._file_names[i] = self._input_files[i].split(self._sep)[-1]
        else:
            self._file_names = file_names

        # convert to list(file_names)
        if not isinstance(self._file_names, str):
            self._file_names = list(self._file_names)
        else:
            self._file_names = [self._file_names]

        # check whether to append k-points or write separate file
        if(k_points_path in self._file_names):
            self._k_mode = 'append'
        else:
            self._k_mode = 'separate'

        # k_points_fct
        if not(hasattr(k_points_fct, '__getitem__') and hasattr(k_points_fct, '__iter__')):
            self._k_points_fct = [k_points_fct]
        else:
            self._k_points_fct = k_points_fct

        self._calling_path = os.getcwd()

        # make input_files absolute (check if already absolute)
        for i in range(len(self._input_files)):
            if not(self._input_files[i][0] == self._sep or
                   self._input_files[i][0] == "~"):  # relative
                self._input_files[i] = self._calling_path + self._sep + \
                    self._input_files[i]

        self._command = command
        self._executable = executable
        if(isinstance(k_points_path, str)):
            self._k_points_path = [k_points_path]
        else:
            self._k_points_path = k_points_path
            
        # check if the number of functions matches the number of paths
        if(len(self._k_points_path) != len(self._k_points_fct)):
            raise ValueError(
                'k_points_fct ({0}) and k_points_path({1}) must have ' +
                'the same length'.format(
                    len(self._k_points_path), len(self._k_points_fct)))
        self._mmn_path = mmn_path
        self._clean_subfolder = clean_subfolder

        self._calling_path = os.getcwd()

        # working folder given as string
        if(isinstance(working_folder, str)):
            self._create_working_folder(working_folder)
        # working folder given as a function of counter
        else:
            self._counter = 0
            self._working_folder_fct = working_folder

    def _create_working_folder(self, working_folder):
        # check all paths: absolute / relative?
        # absolute
        if(working_folder[0] == self._sep or working_folder[0] == "~"):
            self._working_folder = working_folder
        else:  # relative
            self._working_folder = (self._calling_path +
                                    self._sep + working_folder)
        # make file_names absolute (assumed to be relative to working_folder)
        self._file_names_abs = []
        for i in range(len(self._file_names)):
            self._file_names_abs.append(self._working_folder + self._sep +
                                        self._file_names[i])

        self._k_points_path_abs = []
        for path in self._k_points_path:
            self._k_points_path_abs.append(
                self._working_folder + self._sep + path)
        self._mmn_path_abs = self._working_folder + self._sep + self._mmn_path

        # create working folder if it doesn't exist
        if not(os.path.isdir(self._working_folder)):
            subprocess.call("mkdir " + self._working_folder, shell=True)

    def _create_input(self, *args):
        try:
            self._counter += 1
            self._create_working_folder(
                self._working_folder_fct(self._counter))
        except (AttributeError, NameError):
            pass

        if(self._clean_subfolder):
            if not(self._is_windows):
                subprocess.call('rm -rf ' + self._working_folder + self._sep
                                + "*", shell=True)
            else:
                try:
                    subprocess.call('del ' + self._working_folder + self._sep
                                    + '* /S /Q', shell=True)
                except OSError:  # if there is no file to delete
                    pass
                try:
                    subprocess.call('for /d %x in (' + self._working_folder
                                    + self._sep + '*) do rd /S /Q "%x"')
                except OSError:  # if there is no folder to delete
                    pass
        _copy(self._input_files, self._file_names_abs)


        for i, f_path in enumerate(self._k_points_path_abs):
            if(self._k_mode == 'append'):
                f = open(f_path, "a")
            else:
                f = open(f_path, "a")
            f.write(self._k_points_fct[i](*args))
            f.close()

    def _static_run(self, string_dir, string_pos, N):
        start_point = copy.copy(string_pos)
        start_point.insert(string_dir, 0)
        end_point = copy.copy(string_pos)
        end_point.insert(string_dir, 1)
        return self._run(start_point, end_point, N)

    def _run(self, start_point, string_vec, N):
        end_point = [start_point[i] + string_vec[i] for i in range(len(start_point))]
        last_point = [1. / N * start_point[i] +
                      (N - 1.)/float(N) * end_point[i]
                      for i in range(3)]
                      
        # create input
        self._create_input(start_point, last_point, end_point, N)

        # execute command
        if(self._executable is not None):
            subprocess.call(
                self._command,
                cwd=self._working_folder,
                shell=True,
                executable=self._executable)
        else:
            subprocess.call(
                self._command,
                cwd=self._working_folder,
                shell=True)

        # read mmn file
        return mmn.getM(self._mmn_path_abs)

    def _flexible_run(self, plane_edge_start, plane_edge_end, string_vec, kx, N):
        start_point = [(1. - kx) * plane_edge_start[i] + kx * plane_edge_end[i]
                       for i in range(len(plane_edge_start))]
        end_point = [start_point[i] + string_vec[i] for i in range(len(plane_edge_start))]
        return self._run(start_point, end_point, N)


def _copy(initial_paths, final_names):
    """
    copies one or more files to folder

    args:
    ~~~~
    initial_paths:              path to file or list of paths
    final_names:                name(s) or paths (relative to folder)
                                where to copy to
    folder:                     folder to copy into
    """
    if(hasattr(initial_paths, '__iter__') and
       hasattr(initial_paths, '__getitem__') and
       not isinstance(initial_paths, str)):
        for i, initial_path in enumerate(initial_paths):
            _copy(initial_path, final_names[i])
    else:
        shutil.copyfile(initial_paths, final_names)
