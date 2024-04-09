""""Defines the result (data + convergence information) object for surface calculations."""

from .._result import Result

__all__ = ["SurfaceResult"]


class SurfaceResult(Result):
    """Container for the data, state and convergence status of a surface calculation. The attributes / properties of the data object (:class:`SurfaceData`) can be accessed directly from the :class:`SurfaceResult` object.

    Example:

    .. code:: python

        result = z2pack.surface.run(...)
        print(result.t) # prints the positions of the lines
        print(result.pol) # prints the sum of WCC for each line
    """

    @property
    def convergence_report(self):
        r"""
        Convergence report (as a dict) for the result. The keys of the dictionary indicate the type of convergence test. For each of the tests, a dictionary with keys 'PASSED', 'FAILED' and (optionally) 'MISSING' shows the number of tests of this kind which either passed, failed, or were not performed.
        """

        report = {}

        line_report = {}
        line_c_ctrl = set()
        for line in self.lines:
            line_c_ctrl.update(line.ctrl_convergence.keys())
        for c_ctrl in sorted(list(line_c_ctrl)):
            ctrl_report = {}
            passed_t = []
            failed_t = []
            missing_t = []
            for line in self.lines:
                try:
                    if line.ctrl_convergence[c_ctrl]:
                        passed_t.append(line.t)
                    else:
                        failed_t.append(line.t)
                except KeyError:
                    missing_t.append(line.t)
            ctrl_report["PASSED"] = passed_t
            ctrl_report["FAILED"] = failed_t
            ctrl_report["MISSING"] = missing_t
            line_report[c_ctrl] = ctrl_report
        report["line"] = line_report

        surface_report = {}
        for c_ctrl, converged in sorted(self.ctrl_convergence.items()):
            if converged is None:
                ctrl_report = None
            else:
                ctrl_report = {}
                ctrl_report["PASSED"] = []
                ctrl_report["FAILED"] = []
                for t_pair, conv in zip(zip(self.t[:-1], self.t[1:]), converged):
                    if conv:
                        ctrl_report["PASSED"].append(t_pair)
                    else:
                        ctrl_report["FAILED"].append(t_pair)
            surface_report[c_ctrl] = ctrl_report
        report["surface"] = surface_report

        return report
