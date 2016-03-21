.. image:: images/z2pack_logo.svg
    :width: 200px
    :alt: Z2Pack

|

.. container:: section

    is a tool for calculating topological invariants. The method is based on tracking the evolution of hybrid Wannier functions, which is equivalent to the computation of the Wilson loop. Originally developed for calculating :math:`\mathbb{Z}_2` invariants, it is now also capable of calculating Chern numbers. Moreover, through the use of individual Chern numbers it can be used to identify **any kind** of topological phase.

    A key feature of Z2Pack is its **flexibility**: It can be used with various kinds of calculations and models. Currently, interfaces to **first-principles codes**, **tight-binding** models and :math:`\mathbf{k \cdot p}` models are implemented. However, it can in principle be extended to any kind of system.

    .. rubric:: Please cite

    * Dominik Gresch, Alexey A. Soluyanov, G. Autès, O. V. Yazyev, B. Andrei Bernevig, David Vanderbilt, and Matthias Troyer "Universal framework for identifying topological materials and its numerical implementation" [in preparation]
    * Alexey A. Soluyanov and David Vanderbilt "Computing topological invariants without inversion symmetry" [`PhysRevB.83.235401 <http://dx.doi.org/10.1103/PhysRevB.83.235401>`_]


News
====

.. rubric:: Version 1.1 released

Z2Pack version 1.1 is now available! Changes include:

* functions for calculating Chern numbers
* arbitrary surfaces are now possible with tight-binding models
* tight-binding Hamiltonians can now be explicitly specified

Tutorial & Examples
===================
.. toctree::
    :maxdepth: 2
    
    tutorial.rst
    examples.rst

Documentation
=============
.. toctree::
    :maxdepth: 2

    core.rst
    helpers.rst
    fp.rst
    tb.rst

.. ~ .. toctree::
.. ~     :hidden:
.. ~ 
.. ~     genindex </genindex.html>


Getting in touch
================
The development version of Z2Pack is hosted on `GitHub`_ .
Post an `issue <https://github.com/Z2PackDev/Z2Pack/issues>`_ there or contact `me`__ directly with questions / suggestions
/ feedback about Z2Pack.

__ dg_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

.. _dg: http://github.com/greschd
.. _GitHub: http://github.com/Z2PackDev/Z2Pack
