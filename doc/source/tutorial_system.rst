.. _z2pack_tutorial_system :

Creating a Z2Pack System
========================

The first step in creating a calculation with Z2Pack is to define the system which you are going to study. Currently, there are three different types of systems or models available:

.. contents::
    :local:

Models with an explicit Hamiltonian matrix - :mod:`z2pack.hm`
-------------------------------------------------------------

The simplest way of creating a system is when it can be explicitly described by a Hamiltonian matrix :math:`\mathcal{H}(\mathbf{k})`. For example, an effective model for an isotropic Weyl point is given by

.. math ::

    \mathcal{H}(\mathbf{k}) = \sum_{i\in \{x, y, z\}} k_i \cdot \sigma_i

The class :class:`z2pack.hm.System` is constructed by passing the function which describes this Hamiltonian as the first argument:

.. code :: python

    import z2pack
    import numpy as np
    
    def hamiltonian(k):
        kx, ky, kz = k
        return np.array([
            [kz, kx - 1j * ky],
            [kx + 1j * ky, -kz]
        ])
    
    system = z2pack.hm.System(hamiltonian)
    
By default, the lower-lying half of the states will be used for constructing the Wilson loop and Wannier charge centers. In this case, since the matrix has size 2, only the lowest band contributes. This behaviour can be changed by setting the ``bands`` keyword in the constructor. Either the number of "occupied" states can be given, or the relevant bands can be selected by index.

This means that

.. code :: python
    
    system = z2pack.hm.System(hamiltonian, bands=2)
    
includes WCC from both bands, and

.. code :: python
    
    system = z2pack.hm.System(hamiltonian, bands=[1])

includes only the upper band (because the index starts at 0).

.. note ::
    
    Keyword arguments which were not discussed here are described in the :ref:`z2pack_reference`. Throughout this tutorial, only the basic keywords will be covered. Clicking on a method or class name like :class:`z2pack.hm.System` will take you to the relevant section of the reference.

Tight-binding models - :mod:`z2pack.tb`
---------------------------------------

For tight-binding models, the `TBmodels <http://z2pack.ethz.ch/tbmodels>`_ package (which started its life as a part of Z2Pack) is used. TBmodels uses its :py:class:`tbmodels.Model` class to describe a tight-binding model. There are several ways to create those, described in the `TBmodels tutorial <http://z2pack.ethz.ch/tbmodels/tutorial.html>`_ . Instances of  :py:class:`tbmodels.Model` can be used to construct Z2Pack systems, using the :class:`z2pack.tb.System` class.

The following code shows how to create a Z2Pack system from a tight-binding model given in Wannier90's ``*_hr.dat`` format.

.. code :: python

    import z2pack
    import tbmodels
    
    model = tbmodels.Model.from_hr_file('path_to_directory/wannier90_hr.dat')
    system = z2pack.tb.System(model)

First-principles calculations - :mod:`z2pack.fp`
------------------------------------------------

In order to calculate topological invariants reliably using first-principles, Z2Pack needs to dynamically make calls to the first-principles code. This means that one must provide a way of calling the first-principles code automatically from within Z2Pack. The :class:`z2pack.fp.System` class aims to make this as simple as possible.

There are four steps involved in each call to a first-principles code: 

1. Input files created by the user are copied into the working folder
#. A string specifying the k - points is either appended to one of those files or put in a separate file
#. The first - principles code is called and Wannier90 creates the ``.mmn`` file
#. Z2Pack reads the overlap matrices from the ``.mmn`` file

1. Preparing input files
~~~~~~~~~~~~~~~~~~~~~~~~

For the first step, the user needs to create input files for an NSCF run calling Wannier90. These input files should also contain a reference to the density file acquired in a previous SCF run. However, the **k-points** used in the NSCF run should not be in these files. The reason for this is that the k-points will change many times during a Z2Pack calculation.

The Wannier90 input file should contain the ``exclude_bands`` tag to exclude the non-occupied bands. Also, you should make sure that overlaps between neighbouring k-points on the string are computed exactly once, i.e. there are no overlaps computed from one k-point to the neighbour's equivalent point in another unit cell. In most cases this can be done by setting ``shell_list 1``.

If the unit cell is very long in a certain direction, however, it can happend that this setting will just compute overlaps between equivalent points in different unit cells. In that case, you can either add more k-points to the string (costly!) or set the parameter ``search_shells`` instead. It should be large enough s.t. the direct neighbours are included, but not so large that the neighbour's equivalent points are included.

.. note::
    As of yet, it is not possible to add k-points that do not belong to the string to the calculation. This means HF or metaGGA calculations cannot be done. We are planning on fixing that, though.

When creating the :class:`z2pack.fp.System` instance, the input files should be listed in the ``input_files`` keyword argument (as a list of strings).

2. Preparing k-points input
~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you are using  **VASP**, **ABINIT** or **Quantum Espresso**, you can use the functions provided in :mod:`z2pack.fp.kpoint` to create k-points input. Else, you will need to specify a function producing the input for specifying the k-points.

In both cases, the function itself should be given as the ``kpts_fct`` input variable, while the file the k-points string should be printed to is given as ``kpts_path``. If you need the k-points input to be written to more than one file, you can let ``kpts_fct`` be a list of functions, and ``kpts_path`` a list of file names.

The function given in ``kpt_fct`` must have the following syntax:

::

    def function_name(kpt):
        ...
        return string

where ``kpt`` is a ``list`` containing the desired k-points *including* the periodic image of the first point. Hence to compute a string with ``N`` k-points, ``N + 1`` points are given, and the last point is a periodic image of the first. Note thus that the function should be constructed in such a way that the first-principles code will not use the last point in its calculation. 

3. Call to the first-principles code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The call to the first-principles code is simple: just provide Z2Pack with the command line input (as a string) of how to call the first-principles code you are using. This is the ``command`` keyword argument to :class:`fp.System`.

4. Reading the .mmn file
~~~~~~~~~~~~~~~~~~~~~~~~
Finally, Z2Pack needs the path to where the overlap file ``wannier90.mmn`` will be (Keyword argument ``mmn_path``). By default, it is assumed to be in the top level of the build directory.

Combining these four steps, we get the following example (for VASP):

.. code :: python

    system = z2pack.fp.System(
        input_files=[
            "input/CHGCAR", 
            "input/INCAR", 
            "input/POSCAR", 
            "input/POTCAR", 
            "input/wannier90.win" 
        ],                              # Step 1
        kpt_fct=z2pack.fp.kpoint.vasp,  # Step 2
        kpt_path="KPOINTS",             # Step 2
        command="mpirun $VASP >& log",  # Step 3
        mmn_path='wannier90.mmn'        # Step 4 (this is the default setting)
    )


Now that you know how to construct the various systems, it's time to get to work: :ref:`Let's run some calculations! <z2pack_tutorial_surface>`
