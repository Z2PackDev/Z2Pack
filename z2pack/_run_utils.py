"""
Helper functions to create common tasks in different run methods (line, surface, volume).
"""

import os
import time

from decorator import decorator

__all__ = []


def _log_run(logger):
    """
    Log the inputs, elapsed time and convergence report for a calculation run.
    """

    def inner(fct, **kwargs):  # pylint: disable=missing-docstring
        logger.info(kwargs, tags=('setup', 'box', 'skip'))
        start_time = time.time()

        result = fct(**kwargs)

        end_time = time.time()
        logger.info(
            end_time - start_time, tags=('box', 'skip-before', 'timing')
        )
        logger.info(
            result.convergence_report, tags=('convergence_report', 'box')
        )

        return result

    return decorator(inner)


def _load_init_result(
    *, init_result, save_file, load, load_quiet, serializer, valid_type
):
    """
    Load the initial result from a given save file.

    :param init_result: Initial result. If the result is already given, it is not allowed to also load the result.
    :type init_result: :class:`Result`

    :param load: Determines whether the initial result is loaded from ``save_file``.
    :type load: bool

    :param load_quiet:  Determines whether errors / inexistent files are ignored when loading from ``save_file``
    :type load_quiet:   bool

    :param serializer:  Serializer which is used to save the result to file. Valid options are :py:mod:`msgpack`, :py:mod:`json` and :py:mod:`pickle`. By default (``serializer='auto'``), the serializer is inferred from the file ending. If this fails, :py:mod:`msgpack` is used.
    :type serializer:   module

    :param valid_type: Valid type for the init_result.
    :type valid_type: type

    :returns: :class:`Result` instance.
    """
    # avoid circular import (solved in Python 3.5 and higher)
    from . import io

    if init_result is not None:
        if load:
            raise ValueError(
                'Inconsistent input parameters "init_result != None" and "load == True". Cannot decide whether to load result from file or use given result.'
            )
    elif load:
        if save_file is None:
            raise ValueError(
                'Cannot load result from file: No filename given in the "save_file" parameter.'
            )
        try:
            init_result = io.load(save_file, serializer=serializer)
        except IOError as exception:
            if not load_quiet:
                raise exception

    if init_result is not None:
        if not isinstance(init_result, valid_type):
            raise ValueError(
                "The initial result has invalid type '{}': should be '{}'".
                format(type(init_result), valid_type)
            )

    return init_result


def _check_save_dir(*, save_file):
    """
    Checks that the directory containing the ``save_file`` exists.
    """
    if save_file is not None:
        dirname = os.path.dirname(os.path.abspath(save_file))
        if not os.path.isdir(dirname):
            raise ValueError('Directory {} does not exist.'.format(dirname))
