"""Defines functions to run a surface calculation."""

import copy
import logging
import contextlib

import numpy as np
from fsc.export import export

from . import _LOGGER
from . import VolumeData
from . import VolumeResult
from ._control import _create_volume_controls, VolumeControlContainer

from .._async_handler import AsyncHandler
from .._run_utils import _load_init_result, _check_save_dir
from .._logging_tools import TagAdapter, TagFilter, filter_manager
_LOGGER = TagAdapter(_LOGGER, default_tags=('volume', ))

from ..surface import _run as _surface_run


@export
def run_volume(
    *,
    system,
    volume,
    pos_tol=1e-2,
    gap_tol=0.3,
    move_tol=0.3,
    num_surfaces=11,
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
    Calculates the Wannier charge centers for a given system and volume.

    * automated convergence in string direction
    * automated check for distance between gap and wcc → add string
    * automated convergence check w.r.t. movement of the WCC between
      different k-strings.

    :param system:      System for which the WCC should be calculated.
    :type system:       :class:`z2pack.system.EigenstateSystem` or :class:`z2pack.system.OverlapSystem`.

    :param volume:      Volume in which the WCC / Wilson loops should be calculated. The argument should be a callable which parametrizes the volume :math:`\mathbf{k}(t_1, t_2, t_3)`, in reduced coordinates. It should take three arguments (``float``) and return a nested list of ``float`` describing the points in k-space. Note that the surface must be closed at least along the :math:`t_3` - direction, that is :math:`\mathbf{k}(t_1, t_2, 0) = \mathbf{k}(t_1, t_2, 1) + \mathbf{G}`, where :math:`\mathbf{G}` is an inverse lattice vector.

    :param pos_tol:     The maximum movement of a WCC for the iteration w.r.t. the number of k-points in a single string to converge. The iteration can be turned off by setting ``pos_tol=None``.
    :type pos_tol:      float

    :param gap_tol:     Determines the smallest distance between a gap and its neighbouring WCC for the gap check to be satisfied. The distance must be larger than ``gap_tol`` times the size of the gap. This check is performed only for the largest gap in each string of WCC. The check can be turned off by setting ``gap_tol=None``.
    :type gap_tol:      float

    :param move_tol:    Determines the largest possible movement between WCC of neighbouring strings for the move check to be satisfied. The movement can be no larger than ``move_tol`` time the size of the largest gap between two WCC (from the two neighbouring strings, the smaller value is chosen). The check can be turned off by setting ``move_tol=None``.
    :type move_tol:    float

    :param num_lines:     Initial number of strings.
    :type num_lines:      int

    :param num_surfaces:  Initial number of surfaces.
    :type num_surfaces:   int

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

    :param serializer:  Serializer which is used to save the result to file. Valid options are :py:mod:`msgpack`, :py:mod:`json` and :py:mod:`pickle`. By default (``serializer='auto'``), the serializer is inferred from the file ending. If this fails, :py:mod:`json` is used.
    :type serializer:   module

    :returns:   :class:`VolumeResult` instance.

    Example usage:

    .. code:: python

        system = ... # Refer to the various ways of creating a System instance.
        result = z2pack.volume.run(
            system=system,
            surface=lambda t1, t2, t3: [t1, t2, t3]
        )
        print(result.wcc) # Prints a nested list of WCC (a list for each surface, which each contains a list of WCC for each line).

    """
    _LOGGER.info(locals(), tags=('setup', 'box', 'skip'))

    #     # setting up controls
    controls = _create_volume_controls(
        pos_tol=pos_tol, iterator=iterator, gap_tol=gap_tol, move_tol=move_tol
    )

    init_result = _load_init_result(
        init_result=init_result,
        save_file=save_file,
        load=load,
        load_quiet=load_quiet,
        serializer=serializer,
        valid_type=VolumeResult,
    )
    _check_save_dir(save_file=save_file)

    return _run_volume_impl(
        *controls,
        system=system,
        volume=volume,
        num_lines=num_lines,
        num_surfaces=num_surfaces,
        min_neighbour_dist=min_neighbour_dist,
        save_file=save_file,
        init_result=init_result,
        serializer=serializer
    )


# filter out LogRecords tagged as 'surface_only' in the surface.
@filter_manager(   # noqa
    logging.getLogger('z2pack.surface'),
    TagFilter(('surface_only', ))
) # noqa
def _run_volume_impl(
    *controls,
    system,
    volume,
    num_lines,
    num_surfaces,
    min_neighbour_dist,
    save_file=None,
    init_result=None,
    serializer='auto'
):
    r"""Implementation of the volume's run.

    :param controls: Control objects which govern the iteration.
    :type controls: AbstractControl

    The other parameters are the same as for :meth:`.run`.
    """
    from .. import io
    ctrl_container = VolumeControlContainer(controls)

    # HELPER FUNCTIONS
    def get_surface(s, init_surface_result=None):
        """
        Runs a line calculation and returns its result.
        """
        # pylint: disable=protected-access
        return _surface_run._run_surface_impl(
            *copy.deepcopy(ctrl_container.surface),
            system=system,
            surface=lambda t1, t2: volume(s, t1, t2),
            num_lines=num_lines,
            min_neighbour_dist=min_neighbour_dist,
            init_result=init_surface_result
        )

    # setting up async handler
    if save_file is not None:

        def handler(res):
            _LOGGER.info(
                'Saving volume result to file {} (ASYNC)'.format(save_file)
            )
            io.save(res, save_file, serializer=serializer)
    else:
        handler = None

    with AsyncHandler(handler) as save_thread:

        def add_surface(s):
            """
            Adds a surface to the Volume, if it is within min_neighbour_dist of
            the given surfaces.
            """
            # find whether the line is allowed still
            dist = data.nearest_neighbour_dist(s)
            if dist < min_neighbour_dist:
                if dist == 0:
                    _LOGGER.info("Surface at s = {} exists already.".format(s))
                else:
                    _LOGGER.warn(
                        "'min_neighbour_dist' reached: cannot add surface at s = {}".
                        format(s)
                    )
                return VolumeResult(
                    data, ctrl_container.stateful, ctrl_container.convergence
                )

            _LOGGER.info('Adding surface at s = {}'.format(s))
            data.add_surface(s, get_surface(s))

            return update_result()

        def update_result():
            """
            Updates all data controls, then creates the result object, saves it to file if necessary and returns the result.
            """

            # update data controls
            for d_ctrl in ctrl_container.data:
                d_ctrl.update(data)

            result = VolumeResult(
                data, ctrl_container.stateful, ctrl_container.convergence
            )
            save_thread.send(copy.deepcopy(result))

            return result

        def collect_convergence():
            """
            Calculates which neighbours are not converged
            """
            res = np.array([True] * (len(data.surfaces) - 1))
            for c_ctrl in ctrl_container.convergence:
                res &= c_ctrl.converged
            _LOGGER.info(
                'Convergence criteria fulfilled for {} of {} neighbouring surfaces.'.
                format(sum(res), len(res))
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
                        s_ctrl.__class__.__name__
                    ]

            data = init_result.data

            # re-run lines with existing result as input
            _LOGGER.info('Re-running existing surfaces.')
            for surface in data.surfaces:
                _LOGGER.info('Re-running surface for s = {}'.format(surface.s))
                surface.result = get_surface(surface.t, surface.result)
                update_result()

        else:
            data = VolumeData()

        # STEP 2 -- PRODUCE REQUIRED SURFACES
        # create surfaces required by num_surfaces
        _LOGGER.info("Adding surfaces required by 'num_surfaces'.")
        for s in np.linspace(0, 1, num_surfaces):
            result = add_surface(s)

        # STEP 3 -- MAIN LOOP
        num_surfaces = len(data.surfaces)
        conv = collect_convergence()
        while not all(conv):
            # add lines for all non-converged values
            new_s = [(s1 + s2) / 2
                     for (s1, s2), c in zip(zip(data.s, data.s[1:]), conv)
                     if not c]
            for s in new_s:
                result = add_surface(s)

            # check if new lines appeared
            num_surfaces_new = len(data.surfaces)
            if num_surfaces == num_surfaces_new:
                break
            num_surfaces = num_surfaces_new
            conv = collect_convergence()

    return result
