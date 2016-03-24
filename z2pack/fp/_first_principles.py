#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    26.09.2014 22:44:18 CEST
# File:    _first_principles.py

import os
import shutil
import subprocess
import collections.abc

from ..system import OverlapSystem
from . import _read_mmn as mmn


class System(OverlapSystem):
    r"""
    A subclass of :class:`z2pack.System` designed to work with various first-principles codes.

    :param input_files: Path(s) of the input file(s)
    :type input_files:  str or list

    :param kpt_fct:    Function that creates a ``str`` specifying the k-points (in the language of the first-principles code used), given a ``starting_point``, ``last_point``, ``end point`` and number of k-points ``N``. Can also be a ``list`` of functions if k-points need to be written to more than one file.

    :param kpt_path:   Name of the file where the k-points ``str`` belongs. Will append to a file if it matches one of the ``file_names``, and create a separate file else. If ``kpt_fct`` is a ``list``, ``kpt_path`` should also be a list, specifying the path for each of the functions.
    :type kpt_path:    str or list of str

    :param command: Command to execute the first principles code
    :type command:  str

    :param build_folder:    Folder where the calculation is executed.
    :type build_folder:     str

    :param executable:  Sets the executable executing the command. If nothing is specified, the ``subprocess`` default will be used.
    :type executable:   str

    :param file_names:  Name(s) the input file(s) should get in the ``build_folder``. Default behaviour is taking the filenames from the input files.
    :type file_names:   str or list

    :param mmn_path:    Path to the ``.mmn`` output file of ``Wannier90``
    :type mmn_path:     str

    :param clean_build: Toggles deleting the content of `build_folder`` before starting a new calculation.
    :type clean_build:  bool

    .. note:: ``input_files`` and ``build_folder`` can be absolute or relative paths, the rest is relative to ``build_folder``
    """
    def __init__(
            self,
            *,
            input_files,
            kpt_fct,
            kpt_path,
            command,
            executable=None,
            build_folder='build',
            file_names='copy',
            mmn_path='wannier90.mmn',
            clean_build=True
    ):
        # convert to lists (input_files)
        if not isinstance(input_files, str):
            self._input_files = list(input_files)
        else:
            self._input_files = [input_files]

        # copy to file_names and split off the name
        if file_names == 'copy':
            self._file_names = [os.path.basename(filename) for filename in self._input_files]
        else:
            self._file_names = file_names

        # kpt_fct
        if isinstance(kpt_fct, collections.abc.Callable):
            self._kpt_fct = [kpt_fct]
        else:
            self._kpt_fct = kpt_fct

        # make input_files absolute (check if already absolute)
        for i, filename in enumerate(self._input_files):
            self._input_files[i] = os.path.abspath(filename)

        self._command = command
        self._executable = executable
        if isinstance(kpt_path, str):
            self._kpt_path = [kpt_path]
        else:
            self._kpt_path = kpt_path

        # check whether to append k-points or write separate file
        self._k_mode = ['a' if path in self._file_names else 'w' for path in self._kpt_path]

        # check if the number of functions matches the number of paths
        if len(self._kpt_path) != len(self._kpt_fct):
            raise ValueError(
                'kpt_fct ({0}) and kpt_path({1}) must have the same length'.format(
                    len(self._kpt_path), len(self._kpt_fct)
                )
            )
        self._mmn_path = mmn_path
        self._clean_build = clean_build

        self._calling_path = os.getcwd()

        # working folder given as string
        if isinstance(build_folder, str):
            self._build_folder = build_folder
            self._create_build_folder()
        # working folder given as a function of counter
        else:
            self._counter = 0
            self._build_folder_fct = build_folder

    def _create_build_folder(self):
        # check all paths: absolute / relative?
        # absolute
        self._build_folder = os.path.abspath(self._build_folder)
        # make file_names absolute (assumed to be relative to build_folder)
        self._file_names_abs = []
        for filename in self._file_names:
            self._file_names_abs.append(self._build_folder + '/' + filename)

        self._kpt_path_abs = []
        for path in self._kpt_path:
            self._kpt_path_abs.append(self._build_folder + '/' + path)
        self._mmn_path_abs = self._build_folder + '/' + self._mmn_path

        # create working folder if it doesn't exist
        if not os.path.isdir(self._build_folder):
            os.mkdir(self._build_folder)

    def _create_input(self, *args):
        try:
            self._counter += 1
            self._create_build_folder(
                self._build_folder_fct(self._counter))
        except (AttributeError, NameError):
            pass

        if self._clean_build:
            shutil.rmtree(self._build_folder)
            os.mkdir(self._build_folder)
        _copy(self._input_files, self._file_names_abs)


        for i, (k_mode, f_path) in enumerate(zip(self._k_mode, self._kpt_path_abs)):
            with open(f_path, k_mode) as f:
                f.write(self._kpt_fct[i](*args))

    def get_mmn(self, kpt):
        N = len(kpt) - 1

        # create input
        self._create_input(kpt)

        # execute command
        if self._executable is not None:
            subprocess.call(
                self._command,
                cwd=self._build_folder,
                shell=True,
                executable=self._executable)
        else:
            subprocess.call(
                self._command,
                cwd=self._build_folder,
                shell=True)

        # read mmn file
        M = mmn.get_m(self._mmn_path_abs)
        if len(M) == 0:
            raise ValueError('No overlap matrices were found. Maybe switch from shell_list to search_shells in wannier90.win or add more k-points to the string.')
        if len(M) != N:
            raise ValueError('The number of overlap matrices found is {0}, but should be {1}. Maybe check search_shells in wannier90.win'.format(len(M), N))
        return M

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
    if isinstance(initial_paths, collections.abc.Iterable) and not isinstance(initial_paths, str):
        for i, initial_path in enumerate(initial_paths):
            _copy(initial_path, final_names[i])
    else:
        shutil.copyfile(initial_paths, final_names)
