"""Defines the System class for first-principles calculations."""

import os
import shutil
import subprocess
import contextlib
import collections.abc

from fsc.export import export

from ..system import OverlapSystem
from . import _read_mmn as mmn


@export
class System(OverlapSystem):
    r"""
    System class for systems which are calculated from first principles.

    :param input_files: Paths of the input files.
    :type input_files:  :py:class:`list` of :py:class:`str`

    :param kpt_fct:    Function that creates a ``str`` specifying the k-points (in the language of the first-principles code used), given a ``starting_point``, ``last_point``, ``end point`` and number of k-points ``N``. Can also be a :py:class:`list` of functions if k-points need to be written to more than one file.

    :param kpt_path:   Name of the file where the k-points ``str`` belongs. Will append to a file if it matches one of the ``file_names``, and create a separate file else. If ``kpt_fct`` is a :py:class:`list`, ``kpt_path`` should also be a list, specifying the path for each of the functions.
    :type kpt_path:    :py:class:`str`, or :py:class:`list` thereof

    :param command: Command to execute the first principles code.
    :type command:  str

    :param executable:  Sets the executable executing the command. If nothing is specified, the :py:mod:`subprocess` default will be used.
    :type executable:   str

    :param build_folder:    Folder where the calculation is executed.
    :type build_folder:     str

    :param file_names:  Names the input files should get in the ``build_folder``. Default behaviour is taking the filenames from the input files.
    :type file_names:   :py:class:`list` of :py:class:`str`

    :param mmn_path:    Path to the ``.mmn`` output file of ``Wannier90``
    :type mmn_path:     str

    :param num_wcc:     Number of WCC which should be produced by the system. This parameter can be used to check the consistency of the calculation. By default, no such check is done.
    :type num_wcc:      int

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
        file_names=None,
        mmn_path='wannier90.mmn',
        num_wcc=None
    ):
        # convert to lists (input_files)
        self._input_files = list(input_files)
        self._build_folder = os.path.abspath(build_folder)

        # copy to file_names and split off the name
        if file_names is None:
            self._file_names = [
                os.path.basename(filename) for filename in self._input_files
            ]
        else:
            self._file_names = list(file_names)
        self._file_names = self._to_abspath(self._file_names)

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
        self._kpt_path = self._to_abspath(self._kpt_path)

        # check whether to append k-points or write separate file
        self._k_mode = [
            'a' if path in self._file_names else 'w' for path in self._kpt_path
        ]

        # check if the number of functions matches the number of paths
        if len(self._kpt_path) != len(self._kpt_fct):
            raise ValueError(
                'kpt_fct ({0}) and kpt_path({1}) must have the same length'.
                format(len(self._kpt_path), len(self._kpt_fct))
            )
        self._mmn_path = self._to_abspath(mmn_path)
        self._calling_path = os.getcwd()

        self._num_wcc = num_wcc

    def _to_abspath(self, path):
        """
        Returns a list of absolute paths from a list of paths relative to the build folder, or a single absolute path from a single relative path.
        """
        if isinstance(path, str):
            return os.path.join(self._build_folder, path)
        return [self._to_abspath(p) for p in path]

    def _create_input(self, kpt):
        """
        Create all input file(s).
        """
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(self._build_folder)
        os.mkdir(self._build_folder)
        _copy(self._input_files, self._file_names)

        for i, (k_mode,
                f_path) in enumerate(zip(self._k_mode, self._kpt_path)):
            with open(f_path, k_mode) as f:
                f.write(self._kpt_fct[i](kpt))

    def get_mmn(self, kpt):
        num_kpt = len(kpt) - 1

        # create input
        self._create_input(kpt)

        # execute command
        subprocess.call(
            self._command,
            cwd=self._build_folder,
            shell=True,
            executable=self._executable
        )

        # read mmn file
        overlap_matrices = mmn.get_m(self._mmn_path)
        if not overlap_matrices:
            raise ValueError(
                'No overlap matrices were found. Maybe switch from shell_list to search_shells in wannier90.win or add more k-points to the line.'
            )
        if len(overlap_matrices) != num_kpt:
            raise ValueError(
                'The number of overlap matrices found is {0}, but should be {1}. Maybe check search_shells in wannier90.win'.
                format(len(overlap_matrices), num_kpt)
            )
        if self._num_wcc is not None:
            shape = (self._num_wcc, self._num_wcc)
            for i, overlaps in enumerate(overlap_matrices):
                if overlaps.shape != shape:
                    raise ValueError(
                        'The shape of overlap matrix #{} is {}, but should be {}.'.
                        format(i, overlaps.shape, shape)
                    )

        return overlap_matrices


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
    if isinstance(initial_paths, collections.abc.Iterable
                  ) and not isinstance(initial_paths, str):
        for i, f in zip(initial_paths, final_names):
            _copy(i, f)
    else:
        shutil.copyfile(initial_paths, final_names)
