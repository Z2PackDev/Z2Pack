#!/usr/bin/env python
"""Defines the functions to run a line calculation."""

import contextlib

import numpy as np

from . import _LOGGER, EigenstateLineData, LineResult, OverlapLineData
from .. import io
from .._logging_tools import TagAdapter
from .._run_utils import _check_save_dir, _load_init_result, _log_run
from ._control import LineControlContainer, _create_line_controls

__all__ = ["run_line"]

# tag which triggers filtering when called from the surface's run.
_LINE_ONLY_LOGGER = TagAdapter(
    _LOGGER,
    default_tags=(
        "line",
        "line_only",
    ),
)
_LOGGER = TagAdapter(_LOGGER, default_tags=("line",))


@_log_run(_LINE_ONLY_LOGGER)
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
    serializer="auto",
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

    :param serializer:  Serializer which is used to save the result to file. Valid options are ``msgpack``, :py:mod:`json` and :py:mod:`pickle`. By default (``serializer='auto'``), the serializer is inferred from the file ending. If this fails, ``msgpack`` is used.
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

    # setting up controls
    controls = _create_line_controls(pos_tol=pos_tol, iterator=iterator)

    # setting up init_result
    init_result = _load_init_result(
        init_result=init_result,
        save_file=save_file,
        load=load,
        load_quiet=load_quiet,
        serializer=serializer,
        valid_type=LineResult,
    )
    _check_save_dir(save_file=save_file)

    return _run_line_impl(
        *controls,
        system=system,
        line=line,
        save_file=save_file,
        init_result=init_result,
    )


def _run_line_impl(*controls, system, line, save_file=None, init_result=None, serializer="auto"):
    """
    Implementation of the line's run.

    :param controls: Control objects which govern the iteration.
    :type controls: AbstractControl

    The other parameters are the same as for :meth:`.run`.
    """
    # check if the line function is closed (up to an inverse lattice vector)
    delta = np.array(line(1)) - np.array(line(0))
    if not np.isclose(np.round(delta), delta).all():
        raise ValueError(
            "Start and end points of the line differ by {}, which is not an inverse lattice vector.".format(
                delta
            )
        )

    ctrl_container = LineControlContainer(controls)

    def save():
        if save_file is not None:
            _LOGGER.info(f"Saving line result to file {save_file}")
            io.save(result, save_file, serializer=serializer)

    # initialize stateful and data controls from old result
    if init_result is not None:
        for d_ctrl in ctrl_container.data:
            # not necessary for StatefulControls
            if d_ctrl not in ctrl_container.stateful:
                d_ctrl.update(init_result.data)
        for s_ctrl in ctrl_container.stateful:
            with contextlib.suppress(KeyError):
                s_ctrl.state = init_result.ctrl_states[s_ctrl.__class__.__name__]
        result = LineResult(init_result.data, ctrl_container.stateful, ctrl_container.convergence)
        save()

    # Detect which type of System is active
    if hasattr(system, "get_eig"):
        data_type = EigenstateLineData
        system_fct = system.get_eig
    else:
        data_type = OverlapLineData
        system_fct = system.get_mmn

    def collect_convergence():
        """Collect convergence control results."""
        res = [c_ctrl.converged for c_ctrl in ctrl_container.convergence]
        _LINE_ONLY_LOGGER.info(f"{sum(res)} of {len(res)} line convergence criteria fulfilled.")
        return res

    # main loop
    while not all(collect_convergence()):
        run_options = {}
        for it_ctrl in ctrl_container.iteration:
            try:
                run_options.update(next(it_ctrl))
                _LOGGER.info(
                    f"Calculating line for N = {run_options['num_steps']}",
                    tags=("offset",),
                )
            except StopIteration:
                _LOGGER.warning("Iterator stopped before the calculation could converge.")
                return result

        data = data_type(
            system_fct(
                list(np.array(line(k)) for k in np.linspace(0.0, 1.0, run_options["num_steps"]))
            )
        )

        for d_ctrl in ctrl_container.data:
            d_ctrl.update(data)

        result = LineResult(data, ctrl_container.stateful, ctrl_container.convergence)
        save()

    return result
