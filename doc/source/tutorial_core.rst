Core Module
===========

Tutorial on the core module :mod:`z2pack`.

.. contents::

Getting Z2Pack
--------------
Z2Pack can be installed directly from the Python package index:

``sudo pip install z2pack``

The source code is also available on GitHub_. If you download the source
code, you can either reference it directly in your Python project by
adding

::

    import sys
    sys.path.append('path_to_package')
    import z2pack

.. note:: ``'path_to_package'`` should be the the top-level directory of
    the git repository (``Z2Pack``), not the directory containing the Python
    module (``Z2Pack/z2pack``).

Alternatively, you can **install** it by typing (while in the source directory)

``sudo python setup.py install --record files.txt``

where the ``--record`` flag is used to enable **uninstalling** at a later
time, using

``cat files.txt | xargs rm -rf``

Class :class:`System<z2pack.System>`
------------------------------------
The :class:`System<z2pack.System>` class is used to describe the system for which you
want to calculate topological invariants. If you want to learn how to
create an instance of :class:`System<z2pack.System>`, please refer to its subclasses
:ref:`fp.System<fp_System>` or :ref:`tb.System<tb_System>` (for
:ref:`first-principles<tutorial_fp>` or :ref:`tight-binding<tutorial_tb>` calculations).

In both cases, the :class:`System<z2pack.System>` instance is used to create the
different surfaces on which to compute the Z2 topological invariant.

Creating a :class:`.Surface`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Having defined a system, the next step is creating a surface for which the
Z2 invariant should be calculated. This is done with the :meth:`System.surface`
method.

The basic functionality of :meth:`surface` requires two arguments:
``edge_fct`` and ``string_vec``. The first one, ``edge_fct``,
describes a function

.. math::
    f:~~  &&t &\longrightarrow &~\mathbf{k}\\
        &[0, 1&] &\longrightarrow &~\mathbb{R}^3

which connects the pumping parameter :math:`t` to the edge of the surface.
The surface then extends along ``string_vec`` from that edge.

.. note:: Since the the beginning and end of a k-point string must be
    equivalend k-points, ``string_vec`` must be a reciprocal lattice vector.
    Usually it will be one of the three unit vectors (``[1, 0, 0]``, ``[0, 1, 0]``,
    ``[0, 0, 1]``).

Keyword arguments given to :meth:`.surface` will be used as defaults for
any :meth:`.wcc_calc` call for that Surface.

.. warning:: Different instances of :class:`.Surface` should have different
    paths to the pickle file (keyword argument ``pickle_file``), otherwise they will overwrite each other's data.

Class :class:`.Surface`
-----------------------
The methods of the :class:`.Surface` class is where most of the
functionality of Z2Pack is implemented. They are used for calculations as well as saving, loading and plotting results. 

Calculating the WCC positions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Calculating the Wannier charge centers is (computationally) the most
demanding task. While it will be quite fast for tight-binding models, it
can take anywhere from minutes to hours (or even days for larger systems)
with first-principles calculations.

The calculation of WCC is invoked by the method :meth:`.wcc_calc`.
By default, the WCC are calculated along 11 k-point strings evenly
distributed between :math:`t = 0` and :math:`t=1`. This initial number
of strings can be changed by setting the ``num_strings`` keyword value.

Convergence options
+++++++++++++++++++

* **Convergence of WCC positions along the k-points string (POS CHECK)**

  The number of k-points along a given string is increased until
  the change in WCC positions is below a certain limit ``pos_tol``. 

  The number of k-points used for each step can be adjusted by setting
  the ``iterator`` keyword. Its value must be a Python iterator returning
  integers. For example, ``iterator=range(10, 31, 4)`` would mean the
  number of k-points goes from 10 to 30 in steps of 4.

  Iteration along the string can be turned off by setting ``pos_check=False``.
  The first value yielded by the ``iterator`` is then used as the
  number of k-points used.

  .. note:: Because the WCC cannot be distinguished between iteration
      steps (i.e. we don't know which WCC is which), the WCC have to be
      sorted. However, since the WCC are defined periodically on
      :math:`[0, 1)`, a WCC could cross from  1 to 0 (or vice versa)
      between iteration steps, which would mess up the  sorting. To
      avoid this, the WCC are sorted not from 0 to 1, but from  the
      largest gap between any two WCC (in both iteration steps) onward.
  
* **Distance between the largest gap and neighbouring WCC (GAP CHECK)**
  For a reliable calculation of the Z2 invariant, the middle of the
  largest gap between WCC in a k-point string should not be too close
  to the WCC in its neighbouring strings. If the WCC are closer than
  ``gap_tol``, another string is added in between the two neighbours.

  This check can be disabled by setting ``gap_check=False``
* **Movement of WCC between neighbouring strings (MOVE CHECK)**
  This convergence option checks for the movement of WCC between
  neighbouring strings in the same way the movement of WCC in a single
  string was considered before. The important thing here is that a WCC
  should not fully cross the largest gap in a single step. For this
  reason, the tolerance for WCC movement is defined as a fraction
  ``pos_tol`` of the size of the largest gap between WCC. If the convergence
  criterion fails, another string is again added between the two neighbours.

  If used with an appropriate value of ``move_tol``, this
  test can help focusing the calculation on the important values where
  the WCC change faster.
  
  This check can be disabled by setting ``move_check=False``

* **Minimum distane between neighbouring strings**
  For both the check for distance between the largest gap and its
  neighbouring WCC and the check for movement of WCC, no additional
  string will be added after the distance between two strings has
  reached the value set by ``min_neighbour_dist``.

.. caution:: Even carefully chosen convergence options can sometimes
    lead to false results, especially when the WCC move very quickly
    due to a narrow band gap. 


Getting the results
~~~~~~~~~~~~~~~~~~~

The Z2 invariant can be calculated by calling the :meth:`.invariant()`
method, which returns 0 for topologically trivial surfaces or 1 for
non-trivial ones.

Wannier charge centers, k-points, :math:`\Lambda` matrices etc.
can be extracted by using the :meth:`.get_res()` method. Its return value is
a ``dict`` containing the data.

Saving and loading with ``pickle``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If ``use_pickle=True`` is set for :meth:`.wcc_calc` (or when creating the :class:`.Surface`), the most important results will automatically be
saved into the path given by ``pickle_files``. They can later be extracted
by calling :meth:`.load`

.. note:: **Not all** internal variables of the :class:`.Surface` instance **can
    be pickled**. For example, ``edge_fct`` cannot be saved. For this
    reason, a loaded :class:`Surface` might not always behave exactly the
    same as a fresh one. To make sure everything is set up properly,
    create the :class:`.Surface` with the same arguments as when you
    initially created it. However, there is no need to re-do the costly
    :meth:`.wcc_calc`.


.. _GitHub: http://github.com/Z2PackDev/Z2Pack
.. _first-principles: 
.. _tight-binding: 
