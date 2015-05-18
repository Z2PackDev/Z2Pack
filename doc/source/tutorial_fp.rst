.. _tutorial_fp:

First - Principles Calculations
===============================

Tutorial on the :mod:`z2pack.fp` submodule.

.. contents::

.. _Wannier90_setup:

Setup and Compatibility
-----------------------

For the computation of overlap matrices, Z2Pack uses the Wannier90 software package. This means that Z2Pack can be used with any first - principles code that interfaces to Wannier90. If you are using Wannier90 **version 2.0.1** or higher, it is compatible with Z2Pack if ``skip_B1_tests = .TRUE.`` is set.

For first-principles codes that are not yet compatible with Wannier90 2.0, a modified version of Wannier90 1.2 is available here:

:download:`Wannier90 1.2, modified for ABINIT<downloads/wannier90-1.2.0.1.tar.gz>`
:download:`Wannier90 1.2<downloads/wannier90-1.2.tar.gz>`

.. ~ :download:`Wannier90 2.0<downloads/wannier90-2.0.0.tar.gz>`

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

The Wannier90 input file should contain the ``exclude_bands`` tag to exclude the non-occupied bands. Also, you should make sure that overlaps between neighbouring k-points on the string are computed exactly once, i.e. there are no overlaps computed from one k-point to the neighbour's equivalent point in another unit cell. In most cases this can be done by setting ``shell_list 1``.

If the unit cell is very long in a certain direction, however, it can happend that this setting will just compute overlaps between equivalent points in different unit cells. In that case, you can either add more k-points to the string (costly!) or set the parameter ``search_shells`` instead. It should be large enough s.t. the direct neighbours are included, but not so large that the neighbour's equivalent points are included.

.. note::
    As of yet, it is not possible to add k-points that do not belong to the string to the calculation. This means HF or metaGGA calculations cannot be done. We're planning on fixing that, though.

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

    def function_name(kpt):
        ...
        return string

where ``kpt`` is a ``list`` containing the desired k-points *including* the periodic image of the first point. Hence to compute a string with ``N`` k-points, ``N + 1`` points are given, and the last point is a periodic image of the first. Note thus that the function should be constructed in such a way that the first-principles code will not use the last point in its calculation. 

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

