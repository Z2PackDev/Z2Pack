""""Defines the result (data + convergence information) object for volume calculations."""

from fsc.export import export

from .._result import Result


@export
class VolumeResult(Result):
    """Container for the data, state and convergence status of a volume calculation. The attributes / properties of the data object (:class:`VolumeData`) can be accessed directly from the :class:`VolumeResult` object.

    Example:

    .. code:: python

        result = z2pack.volume.run(...)
        print(result.s) # prints the positions of the surfaces
    """

    @property
    def convergence_report(self):
        r"""
        Convergence report (as a dict) for the result. The keys of the dictionary indicate the type of convergence test. For each of the tests, a dictionary with keys 'PASSED', 'FAILED' and (optionally) 'MISSING' shows the number of tests of this kind which either passed, failed, or were not performed.
        """
        return
        report = dict()

        line_report = dict()
        line_c_ctrl = set()
        for line in self.lines:
            line_c_ctrl.update(line.ctrl_convergence.keys())
        for c_ctrl in sorted(list(line_c_ctrl)):
            ctrl_report = dict()
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
            ctrl_report['PASSED'] = passed_t
            ctrl_report['FAILED'] = failed_t
            ctrl_report['MISSING'] = missing_t
            line_report[c_ctrl] = ctrl_report
        report['line'] = line_report

        volume_report = dict()
        for c_ctrl, converged in sorted(self.ctrl_convergence.items()):
            if converged is None:
                ctrl_report = None
            else:
                ctrl_report = dict()
                ctrl_report['PASSED'] = []
                ctrl_report['FAILED'] = []
                for t_pair, conv in zip(
                    zip(self.t[:-1], self.t[1:]), converged
                ):
                    if conv:
                        ctrl_report['PASSED'].append(t_pair)
                    else:
                        ctrl_report['FAILED'].append(t_pair)
            volume_report[c_ctrl] = ctrl_report
        report['volume'] = volume_report

        return report
