.. _VASP:

A first-principles calculation with VASP
========================================

.. warning:

    The Z2Pack to VASP interface is unsupported. Since VASP is a proprietary program that the Z2Pack developers do not have access to, any problems regarding this interface should be directed at VASP support.

    Pull requests which update the example files are welcome.

The following is a very basic calculation of Z2 invariants using **VASP** for Bismuth. The complete example (including input files)
can be found on `GitHub <https://github.com/Z2PackDev/Z2Pack/tree/master/2.1.x/examples/fp/Bi_vasp>`_.

The potential file ``POTCAR`` is not included in the example because it
is subject to VASP's license.

.. warning::
    VASP may add additional bands automatically if the initial number of bands is not divisible by the number of cores used. This will lead to meaningless results, and the number of WCC calculated will be too high. To correct this, the variable ``exclude_bands`` in the Wannier90 input file must be adjusted to account for the additional bands. Alternatively, you may change the number of cores used.

.. include:: ../../../../examples/fp/vasp/Bi/run.py
    :code: python
