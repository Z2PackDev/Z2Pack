#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    26.09.2014 22:44:18 CEST
# File:    first_principles.py

from . import kpts
from .. import Z2PackSystem
from . import read_mmn as mmn

import os
import sys
import copy
import shutil
import subprocess


#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                    FIRST PRINCIPLES SPECIALISATION                    #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
class System(Z2PackSystem):
    """
    Subclass of Z2PackSystem designed to work with various first - \
    principles codes.

    :param input_files:             Path(s) of the input file(s)
    :type input_files:              str or list

    :param k_points_fct:            Fct that creates a ``str`` specifying \
    the k-points (in the language of the first-principles code used), \
    given a ``starting_point``, ``last_point``, ``end point`` and number \
    of k-points ``N``.

    :param k_points_path:           Name of the file where the k-points \
    ``str`` belongs. Will append to a file if it matches one of the \
    ``file_names``, and create a separate file else. \
    :type k_points_path:            str

    :param working_folder:          Folder where the created input files go
    :type working_folder:           str

    :param command:                 Command to execute the first principles \
    code
    :type command:                  str

    :param file_names:              Name(s) the input file(s) should get \
    in the ``working_folder``. Default behaviour is taking the filenames \
    from the input files.
    :type file_names:               str or list

    :param mmn_path:                Path to the ``.mmn`` output file of \
    ``Wannier90``
    :type mmn_path:                 str

    :param clean_subfolder:         Toggles deleting the content of \
    ``working_folder`` before starting a new calculation.
    :type clean_subfolder:          bool

    :param kwargs:                  Are passed to the :class:`Z2PackPlane` \
    constructor via :func:`plane`. More recent arguments take precendence.

    .. note:: input_files and working_folder can be absolute or relative \
    paths, the rest is relative to working_folder
    """
    def __init__(self,
                 input_files,
                 k_points_fct,
                 k_points_path,
                 working_folder,
                 command,
                 file_names='copy',
                 mmn_path='wannier90.mmn',
                 clean_working_folder=True,
                 **kwargs):

        self._system = _FirstPrinciplesSystem(input_files,
                                              k_points_fct,
                                              k_points_path,
                                              working_folder,
                                              command,
                                              file_names,
                                              mmn_path,
                                              clean_working_folder)
        self._defaults = kwargs

        def _m_handle_creator_first_principles(string_dir,
                                               plane_pos_dir,
                                               plane_pos):
            # check if kx is before or after plane_pos_dir
            if(3 - string_dir > 2 * plane_pos_dir):
                return lambda kx, N: self._system._run(string_dir,
                                                       [plane_pos, kx],
                                                       N)
            else:
                return lambda kx, N: self._system._run(string_dir,
                                                       [kx, plane_pos],
                                                       N)
        self._m_handle_creator = _m_handle_creator_first_principles


class _FirstPrinciplesSystem:

    def __init__(self,
                 input_files,
                 k_points_fct,
                 k_points_path,
                 working_folder,
                 command,
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

        # convert to lists (input_files, file_names)
        try:
            input_files[0]
            self._input_files = list(input_files)
        except TypeError:
            self._input_files = [input_files]

        if(file_names == 'copy'):
            self._file_names = copy.copy(self._input_files)
        else:
            try:
                file_names[0]
                self._file_names = list(file_names)
            except TypeError:
                self._file_names = [file_names]

        # check whether to append k-points or write separate file
        if(k_points_path in self._file_names):
            self._k_mode = 'append'
        else:
            self._k_mode = 'separate'

        # k_points_fct
        self._k_points_fct = k_points_fct

        self._calling_path = os.getcwd()

        # make input_files absolute (check if already absolute)
        for i in range(len(self._input_files)):
            if not(self._input_files[i][0] == "/" or
                   self._input_files[i][0] == "~"):  # relative
                self._input_files[i] = self._calling_path + '/' + \
                    self._input_files[i]

        self._command = command
        self._k_points_path = k_points_path
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
        if(working_folder[0] == "/" or working_folder[0] == "~"):  # absolute
            self._working_folder = working_folder
        else:  # relative
            self._working_folder = self._calling_path + '/' + working_folder
        # make file_names absolute (assumed to be relative to working_folder)
        self._file_names_abs = []
        for i in range(len(self._file_names)):
            self._file_names_abs.append(self._working_folder + '/' +
                                        self._file_names[i])

        self._k_points_path_abs = (self._working_folder + '/' +
                                   self._k_points_path)
        self._mmn_path_abs = self._working_folder + '/' + self._mmn_path

        # create working folder if it doesn't exist
        if not(os.path.isdir(self._working_folder)):
            subprocess.call("mkdir " + self._working_folder, shell=True)

    def _create_input(self, *args):
        try:
            self._counter += 1
            self._create_working_folder(self._working_folder_fct(self._counter))
        except (AttributeError, NameError):
            pass

        if(self._clean_subfolder):
            subprocess.call("rm -rf " + self._working_folder + "/*",
                            shell=True)
        _copy(self._input_files, self._file_names_abs)

        if(self._k_mode == 'append'):
            f = open(self._k_points_path_abs, "a")
        else:
            f = open(self._k_points_path_abs, "w")
        f.write(self._k_points_fct(*args))

    def _run(self, string_dir, string_pos, N):
        # create input
        start_point = copy.copy(string_pos)
        start_point.insert(string_dir, 0)
        end_point = copy.copy(string_pos)
        end_point.insert(string_dir, 1)
        last_point = [1. / N * start_point[i] +
                      (N - 1.)/float(N) * end_point[i]
                      for i in range(3)]
        self._create_input(start_point, last_point, end_point, N)

        # execute command
        subprocess.call(self._command, cwd=self._working_folder, shell=True)

        # read mmn file
        return mmn.getM(self._mmn_path_abs)


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


if __name__ == "__main__":
    print("first_principles.py")
