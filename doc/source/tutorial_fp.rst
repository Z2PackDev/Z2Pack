.. _tutorial_fp:

First - Principles Calculations
===============================

.. _Wannier90_setup:

Setup and Compatibility
-----------------------

For the computation of overlap matrices, Z2Pack uses the Wannier90 software package. This means that Z2Pack can be used with any first - principles code that interfaces to Wannier90. Unfortunately, the Wannier90 source had to be changed slightly. You can download the modified source here:

:download:`Wannier90 1.2, modified for ABINIT<downloads/wannier90-1.2.0.1.tar.gz>`
:download:`Wannier90 1.2<downloads/wannier90-1.2.tar.gz>`
:download:`Wannier90 2.0<downloads/wannier90-2.0.0.tar.gz>`

.. warning:: Compiling your first-principles code with this version of
    Wannier90 will likely break Wannier90 for purposes other than Z2Pack.
    It is recommended to create a separate instance of the first-principles
    code for Z2Pack.

ABINIT Setup
~~~~~~~~~~~~
The following is a guide on how to install ABINIT with the modified
Wannier90 source. There might be a more straightforward way by linking
to an already compiled source, but this is the easiest procedure we could
come up with.

* **Step 1**

  Download the modified Wannier90 source and copy it to the ``tarballs``
  directory of ABINIT (usually ``~/.abinit/tarballs``)
* **Step 2**

  Now we need to change the checksum ABINIT expects from the Wannier90
  source.
    
    * Get the md5sum for both the original (un-modified) Wannier90 source
      and the modified source with the command ``md5sum filename``. 
    * Go to your ABINIT source folder and open the file ``fallbacks/configure``.
      Search and replace every instance of the old checksum with the new
      one. You should find 2 checksums to replace.

* **Step 3**

  Build ABINIT with Wannier90 enabled. If one of the previous steps
  were not done correctly, the installation will likely get stuck trying to
  download Wannier90.

VASP Setup
~~~~~~~~~~
For VASP, the installation routine doesn't differ from installing VASP with
a regular version of Wannier90. Compile the modified Wannier90 source and
link to it when installing VASP.


Basic Idea
----------
The basic steps of a Wannier charge center calculation with Z2Pack are:

1. Input files created by the user are copied into the working folder
#. A string specifying the k - points is either appended to one of those files or put in a separate file
#. The first - principles code is called and Wannier90 creates the .mmn file
#. Z2Pack reads the overlap matrices from the ``.mmn`` file

For the first step, the user needs to create input files for an NSCF run calling Wannier90. These input files should also contain a reference to the density file acquired in a previous SCF run. However, the **k-points** used in the NSCF run should not be in these files. The reason for this is that the k-points will change many times during a Z2Pack calculation.

.. note::
    The Wannier90 input file must contain the variable ``shell_list 1``. Also, use ``exclude_bands`` to exclude the non - occupied bands.

For the second step, a function that produces the input specifying the k-points is needed. This function must have the following syntax:

::

    def function_name(start_point, last_point, end_point, N):
        ...
        return string

===============   ==========================  =========================
variable name     description                 format
===============   ==========================  =========================
``start_point``   First k - point             ``[float, float, float]``
---------------   --------------------------  -------------------------
``last_point``    Last k - point              ``[float, float, float]``
---------------   --------------------------  -------------------------
``end_point``      start_point + string_vec   ``[float, float, float]``
---------------   --------------------------  -------------------------
``N``               number of k-points        ``int``
===============   ==========================  =========================


.. _fp_System:

Class :class:`.fp.System`
-------------------------
