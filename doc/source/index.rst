.. image:: images/z2pack_logo.svg
    :width: 200px
    :alt: Z2Pack

|

.. title:: Overview

.. container:: section

    is a tool for calculating topological invariants. The method is based on tracking the evolution of hybrid Wannier functions, which is equivalent to the computation of the Wilson loop. Originally developed for calculating :math:`\mathbb{Z}_2` invariants, it is now also capable of calculating Chern numbers. Moreover, through the use of individual Chern numbers it can be used to identify **any kind** of topological phase.

    A key feature of Z2Pack is its **flexibility**: It can be used with various kinds of calculations and models. Currently, interfaces to **first-principles codes**, **tight-binding** models and :math:`\mathbf{k \cdot p}` models are implemented. However, it can in principle be extended to any kind of system.
    
    This is the second major release of Z2Pack. Read :ref:`here<z2pack_tutorial_new>` what's new, and find out which version is best for you.

    .. rubric:: Please cite

    * Dominik Gresch, Alexey A. Soluyanov, G. Autès, O. V. Yazyev, B. Andrei Bernevig, David Vanderbilt, and Matthias Troyer "Universal framework for identifying topological materials and its numerical implementation" [in preparation]
    * Alexey A. Soluyanov and David Vanderbilt "Computing topological invariants without inversion symmetry" [`PhysRevB.83.235401 <http://dx.doi.org/10.1103/PhysRevB.83.235401>`_]


.. rubric:: Parts of the documentation

| :ref:`z2pack_tutorial`
| start here
|
| :ref:`z2pack_examples`
| feel free to copy and paste
|
| :ref:`z2pack_reference`
| detailed description of the classes and functions
|
| :ref:`z2pack_links`
| where to go next
|

.. rubric:: Getting in touch

The development version of Z2Pack is hosted on `GitHub <http://github.com/Z2PackDev/Z2Pack>`_ . Post an issue there or contact `me <http://github.com/greschd>`_ directly with questions / suggestions / feedback about Z2Pack.

.. rubric:: Indices and tables

| :ref:`genindex`
| list of all functions and classes
|
| :ref:`modindex`
| list of all modules and submodules

.. toctree::
    :maxdepth: 2
    :hidden:
    
    tutorial.rst
    examples.rst
    reference.rst
    links.rst
