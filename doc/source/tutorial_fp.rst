.. _tutorial_fp:

First - Principles Calculations
===============================

.. contents::

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
Wannier90 source by replacing the Wannier90 fallback in ABINIT. If your
usual routine is to install ABINIT with Wannier90 as an external (pre-compiled)
library, it may be easier to compile the modified Wannier90 source
again and then linking to that.

* Download the modified Wannier90 source and copy it to the ``tarballs``
  directory of ABINIT (usually ``~/.abinit/tarballs``)
* Now we need to change the checksum ABINIT expects from the Wannier90
  source.
    
    * Get the md5sum for both the original (un-modified) Wannier90 source
      and the modified source with the command ``md5sum filename``. 
    * Go to your ABINIT source folder and open the file ``fallbacks/configure``.
      Search and replace every instance of the old checksum with the new
      one. You should find 2 checksums to replace.

* Build ABINIT with Wannier90 enabled. If one of the previous steps
  were not done correctly, the installation will likely get stuck trying to
  download Wannier90.

VASP Setup
~~~~~~~~~~
For VASP, the installation routine doesn't differ from installing VASP with
a regular version of Wannier90. Compile the modified Wannier90 source and
link to it when installing VASP.

.. _fp_System:

Creating a :class:`fp.System`
-----------------------------
The basic steps of a first-principles WCC calculation with Z2Pack are:

1. Input files created by the user are copied into the working folder
#. A string specifying the k - points is either appended to one of those files or put in a separate file
#. The first - principles code is called and Wannier90 creates the .mmn file
#. Z2Pack reads the overlap matrices from the ``.mmn`` file

1. Preparing input files
~~~~~~~~~~~~~~~~~~~~~~~~

For the first step, the user needs to create input files for an NSCF run calling Wannier90. These input files should also contain a reference to the density file acquired in a previous SCF run. However, the **k-points** used in the NSCF run should not be in these files. The reason for this is that the k-points will change many times during a Z2Pack calculation.

.. note::
    The Wannier90 input file must contain the variable ``shell_list 1``. Also, use ``exclude_bands`` to exclude the non - occupied bands.

When creating the :class:`z2pack.System` instance, the input files should
be listed in the ``input_files`` keyword argument (as a list of strings).

2. Preparing k-points input
~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you are using  **VASP**, **ABINIT** or **Quantum Espresso**, you
can use the functions provided in :mod:`z2pack.fp.kpts` to create k-points
input. Else, you will need to specify a function producing the input for specifying
the k-points.

In both cases, the function itself should be given as the
``kpts_fct`` input variable, while the file the k-points string should
be printed to is given as ``kpts_path``. If you need the k-points input
to be written to more than one file, you can let ``kpts_fct`` be a list
of functions, and ``kpts_path`` a list of file names.

The function given in ``kpt_fct`` must have the following syntax:

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



Depending on how your first-principles code works, it might be easier
to use either ``last_point`` or ``end_point``. Note that ``end_point``
itself should not be in the k-points used.

+----------------------------------------+--------------------------------+
|sample input                            |   desired k-points             |
+=================+======================+================================+
|``start_point``  | ``[0, 0.5, 0]``      |``[0, 0.5, 0], [0, 0.5, 0.2]``  |
+-----------------+----------------------+                                |
|``last_point``   | ``[0, 0.5, 0.8]``    |``[0, 0.5, 0.4], [0, 0.5, 0.6]``|
+-----------------+----------------------+                                |
|``end_point``    |``[0, 0.5, 1]``       |                                |
+-----------------+----------------------+``[0, 0.5, 0.8]``               |
|``N``            |  ``5``               |                                |
+-----------------+----------------------+--------------------------------+

3. Call to the first-principles code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The call to the first-principles code is simple: just provide Z2Pack with
the command line input (as a string) of how to call the first-principles
code you are using. This is the ``command`` keyword argument to :class:`fp.System`.

4. Reading the .mmn file
~~~~~~~~~~~~~~~~~~~~~~~~
Finally, Z2Pack needs the path to where the overlap file ``wannier90.mmn``
will be (Keyword argument ``mmn_path``). By default, it is assumed to be
in the top level of the build directory.

