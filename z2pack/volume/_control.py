"""Control objects for volume calculations."""

from ..surface._control import _create_surface_controls


def _create_volume_controls(*, pos_tol, iterator, move_tol, gap_tol):
    """
    Create control objects needed for a volume calculation.
    """
    return _create_surface_controls(
        pos_tol=pos_tol, iterator=iterator, move_tol=move_tol, gap_tol=gap_tol
    )
