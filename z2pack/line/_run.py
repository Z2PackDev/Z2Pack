#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Defines the functions to run a line calculation."""

import os
import time
import contextlib

import numpy as np
from fsc.export import export

from . import _LOGGER
from . import LineResult
from . import EigenstateLineData, WccLineData
from ._control import StepCounter, PosCheck, ForceFirstUpdate

from .._control import (
    StatefulControl, IterationControl, DataControl, ConvergenceControl,
    LineControl
)

from .._logging_tools import TagAdapter

# tag which triggers filtering when called from the surface's run.
LINE_ONLY__LOGGER = TagAdapter(
    _LOGGER, default_tags=(
        'line',
        'line_only',
    )
)
_LOGGER = TagAdapter(_LOGGER, default_tags=('line', ))


@export
def run_line(
    *,
    system,
    line,
    pos_tol=1e-2,
    iterator=range(8, 27, 2),
    save_file=None,
    init_result=None,
    load=False,
    load_quiet=True,
    serializer='auto'
):
    r"""
    Calculates the Wannier charge centers for a given system and line, automatically converging w.r.t. the number of k-points along the line.

    :param system:      System for which the WCC should be calculated.
    :type system:       :class:`z2pack.system.EigenstateSystem` or :class:`z2pack.system.OverlapSystem`.

    :param line:        Line along which the WCC should be calculated. The argument should be a callable which parametrizes the line :math:`\mathbf{k}(t)`, in reduced coordinates. It should take one argument (``float``) and return a list of ``float`` describing the point in k-space. Note that the line must be closed, that is :math:`\mathbf{k}(0) = \mathbf{k}(1) + \mathbf{G}`, where :math:`\mathbf{G}` is an inverse lattice vector.

    :param pos_tol:     The maximum movement of a WCC for the iteration w.r.t. the number of k-points in a single string to converge. The iteration can be turned off by setting ``pos_tol=None``.
    :type pos_tol:      float

    :param iterator:    Generator for the number of points in a k-point string. The iterator should also take care of the maximum number of iterations. It is needed even when ``pos_tol=None``, to provide a starting value.

    :param save_file:   Path to a file where the result should be stored.
    :type save_file:    str

    :param init_result: Initial result which is loaded at the start of the calculation.
    :type init_result:  :class:`LineResult`

    :param load:        Determines whether the initial result is loaded from ``save_file``.
    :type load:         bool

    :param load_quiet:  Determines whether errors / inexistent files are ignored when loading from ``save_file``
    :type load_quiet:   bool

    :param serializer:  Serializer which is used to save the result to file. Valid options are :py:mod:`msgpack`, :py:mod:`json` and :py:mod:`pickle`. By default (``serializer='auto'``), the serializer is inferred from the file ending. If this fails, :py:mod:`msgpack` is used.
    :type serializer:   module

    :returns:   :class:`LineResult` instance.

    Example usage:

    .. code:: python

        system = ... # Refer to the various ways of creating a System instance.
        result = z2pack.line.run(
            system=system,
            line=lambda t: [t, 0, 0] # Line along kx for ky, kz = 0.
        )
        print(result.wcc) # Prints the list of WCC.

    """

    LINE_ONLY__LOGGER.info(locals(), tags=('setup', 'box', 'skip'))
    # This is here to avoid circular import with the Surface (is solved in Python 3.5 and higher)

    from .. import io

    # setting up controls
    controls = []
    controls.append(StepCounter(iterator=iterator))
    if pos_tol is None:
        controls.append(ForceFirstUpdate())
    else:
        controls.append(PosCheck(pos_tol=pos_tol))

    # setting up init_result
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
        except IOError as e:
            if not load_quiet:
                raise e

    if save_file is not None:
        dirname = os.path.dirname(os.path.abspath(save_file))
        if not os.path.isdir(dirname):
            raise ValueError('Directory {} does not exist.'.format(dirname))

    return _run_line_impl(
        *controls,
        system=system,
        line=line,
        save_file=save_file,
        init_result=init_result
    )


def _run_line_impl(
    *controls,
    system,
    line,
    save_file=None,
    init_result=None,
    serializer='auto'
):
    """
    Implementation of the line's run.

    :param controls: Control objects which govern the iteration.
    :type controls: AbstractControl

    The other parameters are the same as for :meth:`.run`.
    """
    # This is here to avoid circular import with the Surface (is solved in Python 3.5 and higher)
    from .. import io

    start_time = time.time()  # timing the run

    # check if the line function is closed (up to an inverse lattice vector)
    delta = np.array(line(1)) - np.array(line(0))
    if not np.isclose(np.round_(delta), delta).all():
        raise ValueError(
            'Start and end points of the line differ by {}, which is not an inverse lattice vector.'.
            format(delta)
        )

    # check if all controls are valid
    for ctrl in controls:
        if not isinstance(ctrl, LineControl):
            raise ValueError(
                '{} control object is not a LineControl instance.'.
                format(ctrl.__class__)
            )

    # filter controls by type
    def filter_ctrl(ctrl_type):
        return [ctrl for ctrl in controls if isinstance(ctrl, ctrl_type)]

    stateful_ctrl = filter_ctrl(StatefulControl)
    iteration_ctrl = filter_ctrl(IterationControl)
    data_ctrl = filter_ctrl(DataControl)
    convergence_ctrl = filter_ctrl(ConvergenceControl)

    def save():
        if save_file is not None:
            _LOGGER.info('Saving line result to file {}'.format(save_file))
            io.save(result, save_file, serializer=serializer)

    # initialize stateful and data controls from old result
    if init_result is not None:
        for d_ctrl in data_ctrl:
            # not necessary for StatefulControls
            if d_ctrl not in stateful_ctrl:
                d_ctrl.update(init_result.data)
        for s_ctrl in stateful_ctrl:
            with contextlib.suppress(KeyError):
                s_ctrl.state = init_result.ctrl_states[s_ctrl.__class__.
                                                       __name__]
        result = LineResult(init_result.data, stateful_ctrl, convergence_ctrl)
        save()

    # Detect which type of System is active
    if hasattr(system, 'get_eig'):
        DataType = EigenstateLineData
        system_fct = system.get_eig
    else:
        DataType = WccLineData.from_overlaps
        system_fct = system.get_mmn

    def collect_convergence():
        res = [c_ctrl.converged for c_ctrl in convergence_ctrl]
        LINE_ONLY__LOGGER.info(
            '{} of {} line convergence criteria fulfilled.'.
            format(sum(res), len(res))
        )
        return res

    # main loop
    while not all(collect_convergence()):
        run_options = dict()
        for it_ctrl in iteration_ctrl:
            try:
                run_options.update(next(it_ctrl))
                _LOGGER.info(
                    'Calculating line for N = {}'.
                    format(run_options['num_steps']),
                    tags=('offset', )
                )
            except StopIteration:
                _LOGGER.warn(
                    'Iterator stopped before the calculation could converge.'
                )
                return result

        data = DataType(
            system_fct(
                list(
                    np.array(line(k))
                    for k in np.linspace(0., 1., run_options['num_steps'])
                )
            )
        )

        for d_ctrl in data_ctrl:
            d_ctrl.update(data)

        result = LineResult(data, stateful_ctrl, convergence_ctrl)
        save()

    end_time = time.time()
    LINE_ONLY__LOGGER.info(
        end_time - start_time, tags=('box', 'skip-before', 'timing')
    )
    LINE_ONLY__LOGGER.info(
        result.convergence_report, tags=('convergence_report', 'box')
    )
    return result
