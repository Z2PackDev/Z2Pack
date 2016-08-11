

Creating a :class:`.Surface`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Having defined a system, the next step is creating a surface for which the
Z2 invariant should be calculated. This is done with the :meth:`System.surface`
method.

A surface can be defined in two ways, either by specifying a ``param_fct``
(parametrization function) which fully describes the surface, or by
giving a one-dimensional parametrization of the edge, and a vector describing
the direction of the surface from that edge.

Method 1
++++++++

For the first method, ``param_fct`` describes a function

.. math::
    f:~~  &&t_1, t_2 &\longrightarrow &~\mathbf{k}\\
        &&[0, 1]^2 &\longrightarrow &~\mathbb{R}^3

that fully parametrizes the surface.

.. warning::    For first-principles calculations, it is recommended to
    use the second method because arbitrary surfaces are not yet
    supported.

.. note::   In order to get meaningful results, you should make sure
    that the surface is periodic in :math:`t_2`, i.e.
    
    .. math::
        f(t_1, 0) = f(t_1, 1) + \mathbf{G}; ~~~~\forall t_1

    where :math:`\mathbf{G}` is a reciprocal lattice vector.

Method 2
++++++++

The second method requires two arguments:
``param_fct`` and ``string_vec``, where ``param_fct`` now
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

Example
+++++++

The surface at :math:`k_2=0`, with strings
along :math:`k_1` (from :math:`0` to :math:`1`) and :math:`k_3` going from :math:`0`
to :math:`0.5` could be set up as follows (Method 1).

.. code:: python

    system = z2pack.System(...)
    system.surface(lambda t1, t2: [t2, 0, t1 / 2.])

or, equivalently (Method 2)

.. code:: python

    system = z2pack.System(...)
    system.surface(lambda t: [0, 0, t / 2.], [1, 0, 0])




Calculating the WCC positions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Calculating the Wannier charge centers is (computationally) the most
demanding task. While it will be quite fast for tight-binding models, it
can take anywhere from minutes to hours (or even days for larger systems)
with first-principles calculations.

The calculation of WCC is invoked by the method :meth:`Surface.wcc_calc()`.
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

  Iteration along the string can be turned off by setting ``pos_tol=None``.
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

  This check can be disabled by setting ``gap_tol=None``
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
  
  This check can be disabled by setting ``move_tol=None``

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

The Z2 invariant can be calculated by calling the :meth:`.z2()`
method, which returns 0 for topologically trivial surfaces or 1 for
non-trivial ones.

The Chern number can be calculated using the :meth:`.chern()` method,
which returns the Chern number, which returns a `dict` containing the
following:

*   ``chern``: The Chern number.
*   ``pol``: The polarization (sum of WCC) for each string of k-points. Because
    the polarization is defined only :math:`\mod 1`, its value is chosen
    to be in :math:`[0, 1)`.
*   ``step``: The change in polarization between different k-point strings.
    It is also defined only up to an integer constant, and is chosen
    s.t. its absolute value is minimized. The Chern number is equal to the
    sum of steps.

.. note:: A good way of estimating the convergence of the Chern number is
    looking at the maximum absolute value in ``step``. The value should
    be well below :math:`0.5`.

Wannier charge centers, k-points, :math:`\Lambda` matrices etc.
can be extracted by using the :meth:`.get_res()<.Surface.get_res>` method. Its return value is
a ``dict`` containing the data.

Saving and loading with
~~~~~~~~~~~~~~~~~~~~~~~~
If ``pickle_file`` is set (not ``None``) for :meth:`Surface.wcc_calc()` (or when creating the :class:`.Surface`), the most important results will automatically be
saved into the path given by ``pickle_file``. They can later be extracted
by calling :meth:`.load`

.. note:: **Not all** internal variables of the :class:`.Surface` instance **can
    be pickled**. For example, ``edge_fct`` cannot be saved. For this
    reason, a loaded :class:`Surface` might not always behave exactly the
    same as a fresh one. To make sure everything is set up properly,
    create the :class:`.Surface` with the same arguments as when you
    initially created it. However, there is no need to re-do the costly
    :meth:`wcc_calc<.Surface.wcc_calc>`.

Restarting a calculation
~~~~~~~~~~~~~~~~~~~~~~~~
When calculating the Wannier charge centers, Z2Pack automatically saves
the progress each time a string of k-points has converged. This allows
restarting a crashed calculation by calling :meth:`.load` before
:meth:`wcc_calc<.Surface.wcc_calc>`.

It can even be used to restart a calculation with more stringent values
for ``pos_tol``, ``gap_tol`` and ``move_tol``. While the k-point strings
that have already been computed will not be affected by this, the
neighbour checks (gap & move check) will be performed again and additional
strings might be added. This is particularly useful to check for convergence
w.r.t. ``gap_tol`` & ``move_tol``.

.. _GitHub: http://github.com/Z2PackDev/Z2Pack
.. _first-principles: 
.. _tight-binding:
.. _PyPI: https://pypi.python.org/pypi/z2pack
