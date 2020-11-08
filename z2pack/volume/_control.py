"""Control objects for volume calculations."""

from .._control import (
    ControlContainer, VolumeControl, SurfaceControl, LineControl,
    StatefulControl, DataControl, ConvergenceControl, IterationControl
)
from ..surface._control import _create_surface_controls


def _create_volume_controls(*, pos_tol, iterator, move_tol, gap_tol):
    """
    Create control objects needed for a volume calculation.
    """
    return _create_surface_controls(
        pos_tol=pos_tol, iterator=iterator, move_tol=move_tol, gap_tol=gap_tol
    )


class VolumeControlContainer(ControlContainer):
    """
    Container for controls used in the surface run.
    """
    def __init__(self, controls):
        super().__init__(
            controls=controls,
            categories={
                'surface': [(SurfaceControl, LineControl)],
                'stateful': [StatefulControl, VolumeControl],
                'data': [DataControl, VolumeControl],
                'convergence': [ConvergenceControl, VolumeControl],
                'iteration': [IterationControl, VolumeControl],
            },
            valid_type=(VolumeControl, SurfaceControl, LineControl)
        )
