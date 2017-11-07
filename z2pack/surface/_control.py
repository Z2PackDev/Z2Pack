"""Control objects for surface calculations."""

from fsc.export import export

from ..line._control import _create_line_controls
from .._control import (
    ControlContainer, DataControl, ConvergenceControl, StatefulControl,
    IterationControl, SurfaceControl, LineControl
)
from .._utils import _get_max_move


@export
class SurfaceControlContainer(ControlContainer):
    def __init__(self, controls):
        super().__init__(
            controls=controls,
            categories={
                'line': [LineControl],
                'stateful': [StatefulControl, SurfaceControl],
                'data': [DataControl, SurfaceControl],
                'convergence': [ConvergenceControl, SurfaceControl],
                'iteration': [IterationControl, SurfaceControl],
            },
            valid_type=(SurfaceControl, LineControl),
        )


@export
class MoveCheck(DataControl, ConvergenceControl, SurfaceControl):
    """
    Performs the check whether the WCC in neighbouring lines have moved too much.
    """

    def __init__(self, *, move_tol):
        self.move_tol = move_tol
        self._converged = None

    @property
    def converged(self):
        return self._converged

    def update(self, data):
        self._converged = [
            _get_max_move(l1.wcc, l2.wcc) <
            self.move_tol * min(l1.gap_size, l2.gap_size)
            for l1, l2 in zip(data.lines[:-1], data.lines[1:])
        ]


@export
class GapCheck(DataControl, ConvergenceControl, SurfaceControl):
    """
    Performs the check whether the largest gap is too close to WCC in neighbouring lines.
    """

    def __init__(self, *, gap_tol):
        self.gap_tol = gap_tol
        self._converged = None

    @property
    def converged(self):
        return self._converged

    def update(self, data):
        self._converged = [
            all(
                abs(w2 - l1.gap_pos) > self.gap_tol * l1.gap_size
                for w2 in l2.wcc
            ) and all(
                abs(w1 - l2.gap_pos) > self.gap_tol * l2.gap_size
                for w1 in l1.wcc
            ) for l1, l2 in zip(data.lines, data.lines[1:])
        ]


def _create_surface_controls(*, pos_tol, iterator, move_tol, gap_tol):
    """
    Helper function to create the control objects needed by a surface calculation.
    """
    controls = _create_line_controls(pos_tol=pos_tol, iterator=iterator)
    if move_tol is not None:
        controls.append(MoveCheck(move_tol=move_tol))
    if gap_tol is not None:
        controls.append(GapCheck(gap_tol=gap_tol))
    return controls
