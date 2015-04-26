An effective 2D model (tight-binding)
=====================================

In this example, we set up a tight-binding model for a quasi - 2D system. We consider 2 - sublattice square lattice with nearest-neighbour (inter-sublattice) and next - nearest - neighbour (intra-sublattice) hopping terms.

Using different parameters ``t1`` and ``t2`` and modifying the ``settings`` (currently they're the default values) can give you a feeling of the different parameters. Try setting ``num_strings`` very low (e.g. 3) and see how the convergence criteria will effect the result.

.. include:: ../../examples/tb/squarelattice/squarelattice.py
    :code: python
