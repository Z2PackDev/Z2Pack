.. _tutorial_tb:

Tight - Binding Calculations
============================

.. contents::

.. _tb_System:

Setting up the :class:`.tb.Hamilton`
------------------------------------
The first task in calculating a tight-binding model is setting up the
model itself. This is done using the :class:`.tb.Hamilton` class. After
the :class:`.tb.Hamilton` instance, atoms are added to the model using
:meth:`.add_atom`. After that, interactions (hopping terms) between
orbitals are added using :meth:`.add_hopping`

.. note:: All positions are to be given **relative to the reduced unit cell**
    vectors. The reduced unit cell vectors themselves are not needed as an input. 

Adding atoms
~~~~~~~~~~~~

Adding interaction terms
~~~~~~~~~~~~~~~~~~~~~~~~


Creating the :class:`.tb.System`
--------------------------------
