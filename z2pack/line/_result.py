""""Defines the result (data + convergence information) object for line calculations."""

from fsc.export import export

from .._result import Result


@export
class LineResult(Result):
    """Container for the data, state and convergence status of a line calculation. The attributes / properties of the data object (:class:`WccLineData` or :class:`EigenstateLineData`) can be accessed directly from the :class:`LineResult` object."""

    @property
    def convergence_report(self):
        r"""
        Convergence report (as a dict) for the result. The keys of the dictionary indicate the type of convergence test, and the values are booleans which are ``True`` if the test converged."""
        return self.ctrl_convergence
