A first-principles calculation with ABINIT
==========================================
The following is a very basic calculation of Z2 invariants using **ABINIT**
for a **generic system**. Before running this calculation, an SCF run is
required to create a density input file.

Because this file will be quite
large, it is recommended not to reference it in ``input_files`` (the first
variable to :class:`.fp.System`), but instead reference to it directly in
the ``.files`` file. This will avoid unnecessary copying.

The input files should be the same as for any NSCF run, except they should
not contain any k-point information and must include a call to Wannier90.
The Wannier90 input file should contain ``shell_list 1`` and use ``exclude_bands``
to exclude non-occupied bands.

Note also that you will have to **change the command** that is used to call
ABINIT to match your system.

.. include:: ../../../../examples/fp/abinit/generic.py 
    :code: python
