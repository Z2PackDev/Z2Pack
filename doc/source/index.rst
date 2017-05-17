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

    * Dominik Gresch, Gabriel Autès, Oleg V. Yazyev, Matthias Troyer, David Vanderbilt, B. Andrei Bernevig, and Alexey A. Soluyanov "Z2Pack: Numerical Implementation of Hybrid Wannier Centers for Identifying Topological Materials" [`PhysRevB.95.075146 <https://doi.org/10.1103/PhysRevB.95.075146>`_]
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
| :ref:`z2pack_developers`
| getting involved
|
| :ref:`z2pack_material`
| slides and exercises from workshops and talks
|
| :ref:`z2pack_links`
| where to go next
|

.. rubric:: Getting in touch

The development version of Z2Pack is hosted on `GitHub <http://github.com/Z2PackDev/Z2Pack>`_ . If you have a suggestion or have found a bug in the code, please post an issue there. For general questions, you can write to the Z2Pack mailing list z2pack@lists.phys.ethz.ch . Send `me <mailto:greschd@gmx.ch?subject=Z2Pack%20mailing%20list%20subscription&body=Hi%20Dominik,%0D%0AI%20would%20like%20to%20subscribe%20to%20the%20Z2Pack%20mailing%20list.>`_ an email if you would like to subscribe to the mailing list.

.. rubric:: Indices and tables

| :ref:`genindex`
| list of all functions and classes
|
| :ref:`modindex`
| list of all modules and submodules

.. toctree::
    :maxdepth: 2
    :hidden:

    tutorial/index.rst
    examples/index.rst
    reference/index.rst
    devguide/index.rst
    other_material.rst
    links.rst
