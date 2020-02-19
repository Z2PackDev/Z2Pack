"""Defines functions to run a surface calculation."""

import copy
import logging
import contextlib

import numpy as np
from fsc.export import export

from . import _LOGGER
from . import SurfaceData, SurfaceResult
from ._control import _create_surface_controls, SurfaceControlContainer

from .. import io
from .._run_utils import _load_init_result, _check_save_dir, _log_run
from .._async_handler import AsyncHandler
from .._logging_tools import TagAdapter, TagFilter, filter_manager
from ..line import _run as _line_run

# tag which triggers filtering when called from the volume's run.
_SURFACE_ONLY_LOGGER = TagAdapter(
    _LOGGER, default_tags=(
        'surface',
        'surface_only',
    )
)
_LOGGER = TagAdapter(_LOGGER, default_tags=('surface', ))


@export
@_log_run(_SURFACE_ONLY_LOGGER)
def run_surface(
    *,
    system,
    surface,
    pos_tol=1e-2,
    gap_tol=0.3,
    move_tol=0.3,
    num_lines=11,
    min_neighbour_dist=0.01,
    iterator=range(8, 27, 2),
    init_result=None,
    save_file=None,
    load=False,
    load_quiet=True,
    serializer='auto'
):
    r"""
    Calculates the Wannier charge centers for a given system and surface.

    * automated convergence in string direction
    * automated check for distance between gap and wcc → add string
    * automated convergence check w.r.t. movement of the WCC between
      different k-strings.

    :param system:      System for which the WCC should be calculated.
    :type system:       :class:`z2pack.system.EigenstateSystem` or :class:`z2pack.system.OverlapSystem`.

    :param surface:     Surface on which the WCC / Wilson loops should be calculated. The argument should be a callable which parametrizes the surface :math:`\mathbf{k}(t_1, t_2)`, in reduced coordinates. It should take two arguments (``float``) and return a nested list of ``float`` describing the points in k-space. Note that the surface must be closed at least along the :math:`t_2` - direction, that is :math:`\mathbf{k}(t_1, 0) = \mathbf{k}(t_1, 1) + \mathbf{G}`, where :math:`\mathbf{G}` is an inverse lattice vector.

    :param pos_tol:     The maximum movement of a WCC for the iteration w.r.t. the number of k-points in a single string to converge. The iteration can be turned off by setting ``pos_tol=None``.
    :type pos_tol:      float

    :param gap_tol:     Determines the smallest distance between a gap and its neighbouring WCC for the gap check to be satisfied. The distance must be larger than ``gap_tol`` times the size of the gap. This check is performed only for the largest gap in each string of WCC. The check can be turned off by setting ``gap_tol=None``.
    :type gap_tol:      float

    :param move_tol:    Determines the largest possible movement between WCC of neighbouring strings for the move check to be satisfied. The movement can be no larger than ``move_tol`` time the size of the largest gap between two WCC (from the two neighbouring strings, the smaller value is chosen). The check can be turned off by setting ``move_tol=None``.
    :type move_tol:    float

    :param num_lines:     Initial number of strings.
    :type num_lines:      int

    :param min_neighbour_dist:  Minimum distance between two strings (no new strings will be added, even if the gap check or move check fails).
    :type min_neighbour_dist:   float

    :param iterator:    Generator for the number of points in a k-point string. The iterator should also take care of the maximum number of iterations. It is needed even when ``pos_tol=None``, to provide a starting value.

    :param save_file:   Path to a file where the result should be stored.
    :type save_file:    str

    :param init_result: Initial result which is loaded at the start of the calculation.
    :type init_result:  :class:`.LineResult`

    :param load:        Determines whether the initial result is loaded from ``save_file``.
    :type load:         bool

    :param load_quiet:  Determines whether errors / inexistent files are ignored when loading from ``save_file``
    :type load_quiet:   bool

    :param serializer:  Serializer which is used to save the result to file. Valid options are ``msgpack``, :py:mod:`json` and :py:mod:`pickle`. By default (``serializer='auto'``), the serializer is inferred from the file ending. If this fails, :py:mod:`json` is used.
    :type serializer:   module

    :returns:   :class:`SurfaceResult` instance.

    Example usage:

    .. code:: python

        system = ... # Refer to the various ways of creating a System instance.
        result = z2pack.surface.run(
            system=system,
            surface=lambda t1, t2: [t1, t2, 0] # kz=0 surface, with lines along ky.
        )
        print(result.wcc) # Prints a nested list of WCC (a list of WCC for each line in the surface).

    """
    # setting up controls
    controls = _create_surface_controls(
        pos_tol=pos_tol, iterator=iterator, gap_tol=gap_tol, move_tol=move_tol
    )

    # setting up init_result
    init_result = _load_init_result(
        init_result=init_result,
        save_file=save_file,
        load=load,
        load_quiet=load_quiet,
        serializer=serializer,
        valid_type=SurfaceResult,
    )
    _check_save_dir(save_file=save_file)

    return _run_surface_impl(
        *controls,
        system=system,
        surface=surface,
        num_lines=num_lines,
        min_neighbour_dist=min_neighbour_dist,
        save_file=save_file,
        init_result=init_result,
        serializer=serializer
    )


# filter out LogRecords tagged as 'line_only' in the line.
@filter_manager(   # noqa
    logging.getLogger('z2pack.line'),
    TagFilter(('line_only', ))
) # noqa
def _run_surface_impl(
    *controls,
    system,
    surface,
    num_lines,
    min_neighbour_dist,
    save_file=None,
    init_result=None,
    serializer='auto'
):
    r"""Implementation of the surface's run.

    :param controls: Control objects which govern the iteration.
    :type controls: AbstractControl

    The other parameters are the same as for :meth:`.run`.
    """

    # CONTROL SETUP
    ctrl_container = SurfaceControlContainer(controls)

    # HELPER FUNCTIONS
    def get_line(t, init_line_result=None):
        """
        Runs a line calculation and returns its result.
        """
        # pylint: disable=protected-access
        return _line_run._run_line_impl(
            *copy.deepcopy(ctrl_container.line),
            system=system,
            line=lambda ky: surface(t, ky),
            init_result=init_line_result
        )

    # setting up async handler
    if save_file is not None:

        def handler(res):
            _LOGGER.info(
                'Saving surface result to file {} (ASYNC)'.format(save_file)
            )
            io.save(res, save_file, serializer=serializer)
    else:
        handler = None

    with AsyncHandler(handler) as save_thread:

        def add_line(t):
            """
            Adds a line to the Surface, if it is within min_neighbour_dist of
            the given lines.
            """
            # find whether the line is allowed still
            dist = data.nearest_neighbour_dist(t)
            if dist < min_neighbour_dist:
                if dist == 0:
                    _LOGGER.info("Line at t = {} exists already.".format(t))
                else:
                    _LOGGER.warning(
                        "'min_neighbour_dist' reached: cannot add line at t = {}"
                        .format(t)
                    )
                return SurfaceResult(
                    data, ctrl_container.stateful, ctrl_container.convergence
                )

            _LOGGER.info('Adding line at t = {}'.format(t))
            data.add_line(t, get_line(t))

            return update_result()

        def update_result():
            """
            Updates all data controls, then creates the result object, saves it to file if necessary and returns the result.
            """

            # update data controls
            for d_ctrl in ctrl_container.data:
                d_ctrl.update(data)

            result = SurfaceResult(
                data, ctrl_container.stateful, ctrl_container.convergence
            )
            save_thread.send(copy.deepcopy(result))

            return result

        def collect_convergence():
            """
            Calculates which neighbours are not converged
            """
            res = np.array([True] * (len(data.lines) - 1))
            for c_ctrl in ctrl_container.convergence:
                res &= c_ctrl.converged
            _LOGGER.info(
                'Convergence criteria fulfilled for {} of {} neighbouring lines.'
                .format(sum(res), len(res))
            )
            return res

        # STEP 1 -- MAKE USE OF INIT_RESULT
        # initialize stateful controls from old result
        if init_result is not None:
            _LOGGER.info("Initializing result from 'init_result'.")
            # make sure old result doesn't change
            init_result = copy.deepcopy(init_result)

            # get states from pre-existing Controls
            for s_ctrl in ctrl_container.stateful:
                with contextlib.suppress(KeyError):
                    s_ctrl.state = init_result.ctrl_states[
                        s_ctrl.__class__.__name__]

            data = init_result.data

            # re-run lines with existing result as input
            _LOGGER.info('Re-running existing lines.')
            for line in data.lines:
                _LOGGER.info('Re-running line for t = {}'.format(line.t))
                line.result = get_line(line.t, line.result)
                update_result()

        else:
            data = SurfaceData()

        # STEP 2 -- PRODUCE REQUIRED STRINGS
        # create lines required by num_lines
        _LOGGER.info("Adding lines required by 'num_lines'.")
        for t in np.linspace(0, 1, num_lines):
            result = add_line(t)

        # STEP 3 -- MAIN LOOP
        num_lines = len(data.lines)
        conv = collect_convergence()
        while not all(conv):
            # add lines for all non-converged values
            new_t = [(t1 + t2) / 2
                     for (t1, t2), c in zip(zip(data.t, data.t[1:]), conv)
                     if not c]
            for t in new_t:
                result = add_line(t)

            # check if new lines appeared
            num_lines_new = len(data.lines)
            if num_lines == num_lines_new:
                break
            num_lines = num_lines_new
            conv = collect_convergence()

    return result
