"""Defines the base class for Z2Pack results (data + convergence information)."""

import abc

__all__ = ["Result"]


class Result(metaclass=abc.ABCMeta):
    """
    Base class for Z2Pack results. Additionally to the data of the calculation, this object also saves the last state and convergence status of the calculation.

    :param data:    Data object of the calculation

    :param stateful_ctrl:   List of StatefulControl objects of the calculation.

    :param convergence_ctrl:    List of ConvergenceControl objects of the calculation.
    """

    def __init__(self, data, stateful_ctrl, convergence_ctrl):
        self.data = data
        ctrl_states = {}
        # save states
        for s_ctrl in stateful_ctrl:
            ctrl_states[s_ctrl.__class__.__name__] = s_ctrl.state
        self.ctrl_states = ctrl_states
        ctrl_convergence = {}
        # save convergence
        for c_ctrl in convergence_ctrl:
            ctrl_convergence[c_ctrl.__class__.__name__] = c_ctrl.converged
        self.ctrl_convergence = ctrl_convergence

    def __getattr__(self, name):
        """Forwards the attribute access to the ``.data`` attribute if attribute lookup fails on this instance (except for the ``data`` and ``convergence_report`` attributes)."""
        if name not in ["data", "convergence_report"]:
            return getattr(self.data, name)
        return super().__getattribute__(name)

    @property
    @abc.abstractmethod
    def convergence_report(self):
        r"""
        Returns a convergence report (as a string) for the result. This report shows whether the convergence options used for calculating this result were satisfied or not.
        """
