.. _z2pack_tutorial_invariants :

Calculating topological invariants
==================================

After you've done all the work to get the result for a surface, calculating topological invariants is really easy:

.. code :: python

    result = z2pack.surface.run(...)
    print(z2pack.invariant.chern(result))   # Prints the Chern number
    print(z2pack.invariant.z2(result))      # Prints the Z2 invariant

As you can see, you simply need to pass the ``result`` to either :func:`z2pack.invariant.chern` or :func:`z2pack.invariant.z2`. That's it.
