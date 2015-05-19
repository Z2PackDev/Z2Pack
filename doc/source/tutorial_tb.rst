.. _tutorial_tb:

Tight - Binding Calculations
============================

Tutorial on the :mod:`z2pack.tb` submodule.

.. contents::

.. _tb_System:

Setting up the :class:`.tb.Hamilton`
------------------------------------
The first task in calculating a tight-binding model is setting up the
model itself. This can be done either manually, from a ``*_hr.dat`` file
produced by Wannier90, or by specifying the matrix Hamiltonian as a function.

Manually creating a Hamiltonian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For manually setting up a Hamiltonian, the :class:`.tb.Hamilton` class is used.
After creating the :class:`.tb.Hamilton` instance, atoms are added to the model using
:meth:`.add_atom`. Finally, hopping terms between orbitals are added using :meth:`.add_hopping`

.. note:: All positions are to be given **relative to the reduced unit cell**
    vectors. The reduced unit cell vectors themselves are not needed as an input. 

Adding atoms
''''''''''''
Adding an atom requires information about both the type of atom (``element``) and its ``position``. In this simplified picture, the element is specified just by providing the orbitals that can be occupied with their respective energies, and the number of electrons.

* ``element``: tuple ``(orbitals, num_electrons)``

  * ``orbitals``: list of orbital energies
  * ``num_electrons``: number of electrons

* ``position``: list of length 3, positions w.r.t. the reduced unit cell
    
Calling the method :meth:`.add_atom` with these parameters adds the specified atom to the model. To simplify adding hoppings, :meth:`.add_atom` returns the atom index. Atoms are indexed by the order of adding them, starting at 0. 

.. note::
    All energies are to be specified in **arbitrary**, but consistent, **units**. A constant (positive) factor on both orbital energies and hopping will not change the output. 

Adding hopping terms
''''''''''''''''''''

The method :meth:`.add_hopping` is used to add hopping terms. 

.. note::
    It is possible, but not advised, to add hopping terms before all
    atoms have been added. 

The first input variable, ``orbital_pairs``, specifies between **which two orbitals** the hopping takes place. It is a tuple (``orbital_1``, ``orbital_2``), where ``orbital_*`` is again a tuple (``atom_index``, ``orbital_index``), where both indices start at 0.
``orbital_pairs`` can also be a list of such tuples, which means that the same hopping will be applied for every pair of orbitals.

The second input variable, ``rec_lattice_vec``, is a list of length 3 specifying in **which unit cell** the second orbital lies (assuming the first one is in the unit cell at the origin).
Again, ``rec_lattice_vec`` can also be a list of such vectors, which means there is a hopping for each of the orbitals lying in one of the specified unit cells. This applies for **all orbital pairs**. If you want to have different orbitals in different unit cells, you will have to create a separate :meth:`.add_hopping`.

The third input variable, ``overlap`` specifies the **strength** of the hopping.

Finally, ``phase`` (a list of float) can be used to give a different (real or complex) **multiplicative factor** for each of the vectors specified in ``rec_lattice_vec``. If no ``phase`` is given, it defaults to 1. If only one ``phase`` is given, it will be the same for all ``rec_lattice_vec``, which is equivalent to multiplying ``overlap`` by that factor.

.. note::
    The complex conjugate of a given hopping term is added automatically.


Hamiltonian from a ``*_hr.dat`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Alternatively, the Hamiltonian can be set up using a file specifying
the overlaps between the orbitals, in the format used by the file
``seedname_hr.dat`` that is created by Wannier90 (see their User Guide
for details).

The class :class:`.tb.HrHamilton` which is used to create such a Hamiltonian
requires the following arguments:

* ``hr_file``: The path to the ``*_hr.dat`` file
* ``num_occ``: The number of occupied bands
* ``positions`` (optional): The position of each orbital w.r.t. the reduced
  unit cell. By default, all orbitals are placed at the origin. This will
  change the individual WCC, but not the overall topology of the system.

Explicit Hamiltonian from a function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Finally, the Hamiltonian can be set up by specifying a function which creates the matrix Hamiltonian, given the wavevector ``k`` as a ``list`` with three entries.

The class :class:`.tb.ExplicitHamilton` which is used to create such a Hamiltonian
requires the following arguments:

* ``hamiltonian``: The function creating the matrix Hamiltonian.
* ``num_occ``: The number of occupied bands
* ``positions`` (optional): The position of each orbital w.r.t. the reduced
  unit cell. By default, all orbitals are placed at the origin. This will
  change the individual WCC, but not the overall topology of the system.

Creating the :class:`.tb.System`
--------------------------------
Given the :class:`.Hamilton` object, creating a tight-binding calculation is simple: The subclass of :class:`z2pack.System`, :class:`z2pack.tb.System` only requires the :class:`Hamilton` instance as a constructor argument. This takes care of all the tight-binding-specific tasks. 
