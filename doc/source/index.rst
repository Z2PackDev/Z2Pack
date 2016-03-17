.. image:: images/z2pack_logo.svg
    :width: 200px
    :alt: Z2Pack

|

.. container:: section

    is a tool for calculating topological invariants. The method is based on tracking the evolution of hybrid Wannier functions, which is equivalent to the computation of the Wilson loop. Originally developed for calculating :math:`\mathbb{Z}_2` invariants, it is now also capable of calculating Chern numbers. Moreover, through the use of individual Chern numbers it can be used to identify **any kind** of topological phase.

    A key feature of Z2Pack is its **flexibility**: It can be used with various kinds of calculations and models. Currently, interfaces to **first-principles codes**, **tight-binding** models and :math:`\mathbf{k \cdot p}` models are implemented. However, it can in principle be extended to any kind of system.

    .. rubric:: Please cite

    * Dominik Gresch, Alexey A. Soluyanov, G. Autés, O. V. Yazyev, B. Andrei Bernevig, David Vanderbilt, and Matthias Troyer "Universal framework for identifying topological materials and its numerical implementation" [in preparation]
    * Alexey A. Soluyanov and David Vanderbilt "Computing topological invariants without inversion symmetry" [`PhysRevB.83.235401 <http://dx.doi.org/10.1103/PhysRevB.83.235401>`_]


Tutorial, Examples and Documentation
====================================
.. toctree::
    :maxdepth: 2
    
    tutorial.rst
    examples.rst
    documentation.rst


Getting in touch
================
The development version of Z2Pack is hosted on `GitHub <http://github.com/Z2PackDev/Z2Pack>`_ . Post an `issue <https://github.com/Z2PackDev/Z2Pack/issues>`_ there or contact `me <http://github.com/greschd>`_ directly with questions / suggestions / feedback about Z2Pack.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

.. toctree::
    :hidden:

    links.rst
