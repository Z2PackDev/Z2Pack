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

    @property  # noqa
    def convergence_report(self):  # noqa
        r"""
        Convergence report (as a dict) for the result. The keys of the dictionary indicate the type of convergence test. For each of the tests, a dictionary with keys 'PASSED', 'FAILED' and (optionally) 'MISSING' shows the number of tests of this kind which either passed, failed, or were not performed.
        """
        report = dict()

        line_report = dict()
        line_c_ctrl = set()
        for line_list in self.lines:
            for line in line_list:
                line_c_ctrl.update(line.ctrl_convergence.keys())
        for c_ctrl in sorted(list(line_c_ctrl)):
            ctrl_report = dict()
            passed_s_t = []
            failed_s_t = []
            missing_s_t = []
            for s, line_list in zip(self.s, self.lines):
                for line in line_list:
                    try:
                        if line.ctrl_convergence[c_ctrl]:
                            passed_s_t.append((s, line.t))
                        else:
                            failed_s_t.append((s, line.t))
                    except KeyError:
                        missing_s_t.append((s, line.t))
            ctrl_report['PASSED'] = passed_s_t
            ctrl_report['FAILED'] = failed_s_t
            ctrl_report['MISSING'] = missing_s_t
            line_report[c_ctrl] = ctrl_report
        report['line'] = line_report

        surface_report = dict()
        surface_c_ctrl = set()
        for surface in self.surfaces:
            surface_c_ctrl.update(surface.ctrl_convergence.keys())
        for c_ctrl in sorted(list(surface_c_ctrl)):
            ctrl_report = dict()
            passed_s = []
            failed_s = []
            missing_s = []
            for surface in self.surfaces:
                try:
                    if surface.ctrl_convergence[c_ctrl]:
                        passed_s.append(surface.s)
                    else:
                        failed_s.append(surface.s)
                except KeyError:
                    missing_s.append(surface.s)
            ctrl_report['PASSED'] = passed_s
            ctrl_report['FAILED'] = failed_s
            ctrl_report['MISSING'] = missing_s
            surface_report[c_ctrl] = ctrl_report
        report['surface'] = surface_report

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
