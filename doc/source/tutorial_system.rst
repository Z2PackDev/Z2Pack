.. _z2pack_tutorial_system :

Creating a Z2Pack System
========================

The first step in creating a calculation with Z2Pack is to define the system which you are going to study. Currently, there are three different types of systems or models available:

.. contents::
    :local:

Effective k•p models - :mod:`z2pack.em`
---------------------------------------

The simplest way of creating a system is by having a k•p model. A Z2Pack system can be created by having a function which describes the matrix Hamiltonian :math:`\mathcal{H}(\mathbf{k})`. For example, an effective model for an isotropic Weyl point is given by

.. math ::

    \mathcal{H}(\mathbf{k}) = \sum_{i\in \{x, y, z\}} k_i \cdot \sigma_i

The class :class:`z2pack.em.System` is constructed by passing the function which describes this Hamiltonian as the first argument:

.. code :: python

    import z2pack
    import numpy as np
    
    def hamiltonian(k):
        kx, ky, kz = k
        return np.array([
            [kz, kx - 1j * ky],
            [kx + 1j * ky, -kz]
        ])
    
    system = z2pack.em.System(hamiltonian)
    
By default, the lower-lying half of the states will be used for constructing the Wilson loop and Wannier charge centers. In this case, since the matrix has size 2, only the lowest band contributes. This behaviour can be changed by setting the ``bands`` keyword in the constructor. Either the number of "occupied" states can be given, or the relevant bands can be selected by index.

This means that

.. code :: python
    
    system = z2pack.em.System(hamiltonian, bands=2)
    
includes WCC from both bands, and

.. code :: python
    
    system = z2pack.em.System(hamiltonian, bands=[1])

includes only the upper band (because the index starts at 0).

.. note ::
    
    Keyword arguments which were not discussed here are described in the :ref:`z2pack_reference`. Throughout this tutorial, only the basic keywords will be covered. Clicking on a method or class name like :class:`z2pack.em.System` will take you to the relevant section of the reference.

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
