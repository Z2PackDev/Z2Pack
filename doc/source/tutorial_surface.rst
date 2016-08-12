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
    
    f(t_1, 0) = f(t_2, 1) + \mathbf{G},
    
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

Convergence options
-------------------



* **Convergence of WCC positions along the k-points string (POS CHECK)**

  The number of k-points along a given string is increased untilthe change in WCC positions is below a certain limit ``pos_tol``. 

  The number of k-points used for each step can be adjusted by setting the ``iterator`` keyword. Its value must be a Python iterator returning integers. For example, ``iterator=range(10, 31, 4)`` would mean the number of k-points goes from 10 to 30 in steps of 4.

  Iteration along the string can be turned off by setting ``pos_tol=None``. The first value yielded by the ``iterator`` is then used as the number of k-points used.

  .. note:: Because the WCC cannot be distinguished between iteration steps (i.e. we don't know which WCC is which), the WCC have to be sorted. However, since the WCC are defined periodically on :math:`[0, 1)`, a WCC could cross from  1 to 0 (or vice versa) between iteration steps, which would mess up the  sorting. To avoid this, the WCC are sorted not from 0 to 1, but from  the largest gap between any two WCC (in both iteration steps) onward.
  
* **Distance between the largest gap and neighbouring WCC (GAP CHECK)**
  
  For a reliable calculation of the Z2 invariant, the middle of the largest gap between WCC in a k-point string should not be too close to the WCC in its neighbouring strings. If the WCC are closer than ``gap_tol``, another string is added in between the two neighbours.

  This check can be disabled by setting ``gap_tol=None``

* **Movement of WCC between neighbouring strings (MOVE CHECK)**
  
  This convergence option checks for the movement of WCC between neighbouring strings in the same way the movement of WCC in a single string was considered before. The important thing here is that a WCC should not fully cross the largest gap in a single step. For this reason, the tolerance for WCC movement is defined as a fraction ``pos_tol`` of the size of the largest gap between WCC. If the convergence criterion fails, another string is again added between the two neighbours.
  
  If used with an appropriate value of ``move_tol``, this test can help focusing the calculation on the important values where the WCC change faster.  This check can be disabled by setting ``move_tol=None``

* **Minimum distane between neighbouring strings**
  For both the check for distance between the largest gap and its neighbouring WCC and the check for movement of WCC, no additional string will be added after the distance between two strings has reached the value set by ``min_neighbour_dist``.

.. caution:: Even carefully chosen convergence options can sometimes lead to false results, especially when the WCC move very quickly due to a narrow band gap. 
