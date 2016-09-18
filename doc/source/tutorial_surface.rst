.. _z2pack_tutorial_surface :

Calculating a Surface
=====================

Basic Syntax
------------

Having defined a system, the next step is to calculate the Wilson loop / Wannier charge centers on some surface in the Brillouin zone. This is done using the :func:`z2pack.surface.run` function. The basic usage of this function is as follows :

.. code :: python

    # create a system first
    system = ...

    result = z2pack.surface.run(
        system=system,
        surface=lambda t1, t2: [t1, t2, 0]
    )

The ``surface`` parameter must be a function 

.. math ::

    f(t_1, t_2), ~~~~ t_i \in [0, 1]
    
which parametrizes the surface. The surface must be periodic in the direction along which the Wilson loop / Wannier charge centers are calculated, which is the :math:`t_2` direction. In mathematical notation

.. math ::
    
    f(t_1, 0) = f(t_1, 1) + \mathbf{G},
    
where :math:`\mathbf{G}` is a reciprocal lattice vector. In the example above, I chose the surface at :math:`k_z=0`. The Wannier charge centers are calculated on lines along the :math:`k_y` direction.

.. note ::
    
    First-principles codes usually don't allow for an arbitrary shape of the surface. For ABINIT for example, each line must be straight. VASP only allows for lines which are straight and parallel to one of the reciprocal lattice directions.

Saving and loading the result
-----------------------------

Unless the calculation is really fast, you probably want to save your results to a file. You can configure Z2Pack to automatically save the results while calculating by setting the ``save_file`` keyword argument

.. code :: python

    result = z2pack.surface.run(
        system=system,
        surface=lambda t1, t2: [t1, t2, 0],
        save_file='path_to_directory/savefile.msgpack'
    )
    
This saves the result in 'path_to_directory/savefile.msgpack' in the :py:mod:`msgpack` format. By changing the file extension to ``.json`` or ``.pickle``, you can change the serializer to :py:mod:`json` or :py:mod:`pickle`. If the file extension is not recognized, :py:mod:`msgpack` will be used as a serializer.

.. note ::  The :py:mod:`pickle` format is probably not right for your purposes. If you want to see why, watch `this PyCon 2014 talk by Alex Gaynor <https://www.youtube.com/watch?v=7KnfGDajDQw>`_.

Since Z2Pack keeps saving the most recent result during the calculation, you can also use this to restart the calculation from a previous point. To do this, all you need to do is to set the ``load`` keyword to ``True``

.. code :: python

    result = z2pack.surface.run(
        system=system,
        surface=lambda t1, t2: [t1, t2, 0],
        save_file='path_to_directory/savefile.msgpack',
        load=True
    )
    
For retrieving this result, you can use the :func:`z2pack.io.load` function:

.. code :: python

    result = z2pack.io.load('path_to_directory/savefile.msgpack')
    
Next we'll talk about convergence. If you can't wait to finally calculate the topological invariants, this might be a good point to :ref:`skip ahead<z2pack_tutorial_invariants>`. Just take this word of caution:

**The narrower the direct band gap is in your system, the more careful you should be to make sure your calculation has converged.**

Convergence options
-------------------

Since the topological invariants are integers, it's not an easy task to check whether they are converged. Z2Pack provides different checks to help make sure you get an accurate result. The checks are in two categories:

* Checking if there are enough k-points along a line, such that the WCC positions are converged (POS CHECK).
* Checking if there are enough lines on the surface (GAP CHECK and MOVE CHECK).

The following sections describe how each of these checks work and how to adjust them.


Convergence of WCC positions along the k-points lines (POS CHECK)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The number of k-points along a given line is increased until the change in WCC positions is below a certain limit ``pos_tol``. 

The number of k-points used for each step can be adjusted by setting the ``iterator`` keyword. Its value must be a Python iterator returning integers. For example, ``iterator=range(10, 31, 4)`` would mean the number of k-points goes from 10 to 30 in steps of 4.

Iteration along the line can be turned off by setting ``pos_tol=None``. The first value yielded by the ``iterator`` is then used as the number of k-points used.

.. note:: Because the WCC cannot be distinguished between iteration steps (i.e. we don't know which WCC is which), the WCC have to be sorted. However, since the WCC are defined periodically on :math:`[0, 1)`, a WCC could cross from  1 to 0 (or vice versa) between iteration steps, which would mess up the  sorting. To avoid this, the WCC are sorted not from 0 to 1, but from  the largest gap between any two WCC (in both iteration steps) onward.

  
Distance between the largest gap and neighbouring WCC (GAP CHECK)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
For a reliable calculation of the Z2 invariant, the middle of the largest gap between WCC in a k-point line should not be too close to the WCC in its neighbouring lines. The limit of how close they can be is adjusted with the ``gap_tol`` keyword. The WCC cannot be closer than ``gap_tol`` times the size of the gap. If this limit is not met, another line is added in between the two existing ones.

This check can be disabled by setting ``gap_tol=None``


Movement of WCC between neighbouring lines (MOVE CHECK)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This convergence option checks for the movement of WCC between neighbouring lines in the same way the movement of WCC in a single line was considered before. The important thing here is that a WCC should not fully cross the largest gap in a single step. For this reason, the tolerance for WCC movement is defined as a fraction ``pos_tol`` of the size of the largest gap between WCC. If the convergence criterion fails, another line is again added between the two neighbours.

If used with an appropriate value of ``move_tol``, this test can help focusing the calculation on the important values where the WCC change faster. As before, this check can be disabled by setting ``move_tol=None``

Minimum distance between neighbouring lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For both the check for distance between the largest gap and its neighbouring WCC and the check for movement of WCC, no additional line will be added after the distance between two lines has reached the value set by ``min_neighbour_dist``.


Initial number of lines
~~~~~~~~~~~~~~~~~~~~~~~

Using the ``num_lines`` keyword, you can change the initial number of lines which will be calculated (before either MOVE CHECK or GAP CHECK are performed). This is especially important if the direct band gap is very narrow at some point on the surface. In that case, the WCC usually move very quickly around that point. If no line passes close to that point, however, it could be that this movement is not detected.

Example code
~~~~~~~~~~~~

Now let's look at how to set all these convergence parameters. The default settings 

.. code :: python

    result = z2pack.surface.run(
        system=system,
        surface=surface
    )
    
are equivalent to the following code:

.. code :: python

    result = z2pack.surface.run(
        system=system,
        surface=surface,
        pos_tol=0.01,
        gap_tol=0.3,
        move_tol=0.3,
        num_lines=11,
        min_neighbour_dist=0.01,
        iterator=range(8, 27, 2)
    )

For example, we might want to start with more lines, and also allow the lines to be closer to each other. This can be done as follows:

.. code :: python 

    result = z2pack.surface.run(
        system=system,
        surface=surface,
        num_lines=101,
        min_neighbour_dist=0.001
    )

After calculating the surface, you can finally reap the rewards and :ref:`calculate the topological invariants <z2pack_tutorial_invariants>`.
