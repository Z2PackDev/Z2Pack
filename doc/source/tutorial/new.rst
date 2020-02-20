.. _z2pack_tutorial_new :

What's new in Z2Pack 2.0
========================

.. rubric :: First, the bad news

Let's get the elephant out of the room: Z2Pack version 2 is **not** backwards compatible to the previous versions. Furthermore, it is compatible only with Python 3.4 or newer. Because I know that it can be frustrating having to re-write your code when some library changes, I hesitated a long while to do this. However, there are now many things that I could solve in a more elegant way and - more importantly - I believe it will be much easier to add features to this new version. If you have code that is already running in the previous version of Z2Pack, or you cannot switch to Python 3.4 yet, here's the deal: I will **keep supporting** the last version of Z2Pack 1.X as long as there is any need for it.

.. rubric :: And now for the good news

I strongly believe that the package has become more well-structured and easier to use. Many of the things that were an afterthought in the previous version, such as how to restart a calculation or calculating just a single line, are now built into the core of Z2Pack. As a result, some of the quirks of the previous version have been eliminated. In the following sections, I will highlight some of the more prominent improvements.

.. rubric :: Tight-binding models on steroids

The previous version of Z2Pack contained a submodule for creating tight-binding models. This module has now matured and became its own package: `TBmodels <https://tbmodels.greschd.ch>`_. Obviously, TBmodels is still compatible with Z2Pack. Among other improvements, evaluating a tight-binding model is now much faster. The improvement is particularly noticeable for first-principles derived tight-binding models which are much larger than other effective models. To give you a rough idea, for one particular model evaluating the Hamiltonian is about **650** times faster.

.. rubric :: Saving results: going away from pickle

Saving results was previously done with the :py:mod:`pickle` module. As I've learned since writing the first version of Z2Pack, there are various reasons why this is not ideal. Most importantly, objects serialized with :py:mod:`pickle` might not be deserializable when one of the modules involved has changed. The full reasoning can be seen in a `PyCon 2014 talk by Alex Gaynor <https://www.youtube.com/watch?v=7KnfGDajDQw>`_ . By switching to ``msgpack`` as a default serializer, this problem is solved.

Another improvement in the saving process is that the calculation continues while the saving is done in a separate thread. This is particularly useful for smaller systems, where the cost of saving might be comparable or even higher than that of creating the results.

Finally, saving is now done in a way that ensures that the files cannot be corrupted, even if the program crashes whilst saving. This is done by first saving to a separate temporary file and then moving that file to replace the previous version.

.. rubric :: New way of calculating the Wannier charge centers

One of the changes at the core of Z2Pack is how Wannier charge centers are calculated. In both versions, they are calculated from a series of overlap matrices :math:`M_0, ..., M_{n-1}`.

In the previous version, a singular value decomposition

.. math ::

    M = V \Sigma W^\dagger

is first performed for each of the overlap matrices. Then the product

.. math ::

    \Lambda = W_{n-1}V_{n-1}^\dagger \cdot ... \cdot W_0 V_0^\dagger,

is calculated, whose eigenvalues :math:`\lambda_i` are connected to the WCC by

.. math ::

    \bar{x}_i = - \frac{\arg(\lambda_i)}{2 \pi}.


In the current version, the overlap matrices are multiplied together to create the Wilson loop

.. math ::

    \mathcal{W} = M_0 \cdot ... \cdot M_{n-1}


whose eigenvalues :math:`w_i` are connected ot the WCC by

.. math ::

    \bar{x}_i = \frac{\arg(w_i)}{2 \pi}.

Both methods converge to the same value for a large number of k-points. However, the second method was found to converge a bit faster. The more important implication of this is that the Wilson loop (and its eigenstates) can now be used for further analysis. One application of this is already in the package, with the WCC plots that are color-coded according to the symmetry expectation value of the Wilson loop eigenstates. I expect more applications of this kind to be possible.

.. rubric :: A better platform to develop and test new ideas

Having a more modular structure, the new version of Z2Pack lends itself to testing new ideas for how topological invariants can be calculated. Some new features are already in planning, and many more will hopefully come in later versions of Z2Pack 2.X.
