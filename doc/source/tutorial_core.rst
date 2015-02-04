Core Module
===========

Getting Z2Pack
--------------
Z2Pack can be installed directly from the Python package index:

``sudo pip install z2pack``

The source code is also available on github_. If you download the source
code, you can either reference it directly in your Python project by
adding

::

    import sys
    sys.path.append('path_to_package')
    import z2pack

or you can **install** it by typing (while in the source directory)

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
`first-principles`_ or `tight-binding`_ calculations).

In both cases, the :class:`System<z2pack.System>` instance is used to create the
different planes on which to compute the Z2 topological invariant.

Creating a :class:`Plane<z2pack.Plane>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class :class:`Plane<z2pack.Plane>`
----------------------------------

Calculating the WCC positions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Getting the results
~~~~~~~~~~~~~~~~~~~
The Z2 invariant can be calculated by calling the ::
method, which returns 0 for topologically trivial planes or 1 for
non-trivial ones.

Wannier charge centers, k-points, :math:`\Lambda` matrices etc.
can be extracted by using the ``.get_res()`` method. Its return value is
a ``dict`` containing the different 

Saving and loading with ``pickle``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. _github: http://github.com/Z2PackDev/Z2Pack
.. _first-principles: tutorial_fp.html
.. _tight-binding: tutorial_tb.html
