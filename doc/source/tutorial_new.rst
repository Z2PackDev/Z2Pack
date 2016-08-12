.. _z2pack_tutorial_new :

What's new in Z2Pack 2.0
========================

.. rubric :: First, the bad news

Let's get the elephant out of the room: Z2Pack version 2 is **not** backwards compatible to the previous versions. Furthermore, it is compatible only with Python 3.4 or newer. Because I know that it can be frustrating having to re-write your code when some library changes, I hesitated a long while to do this. However, there are now many things that I could solve in a more elegant way and - more importantly - I believe it will be much easier to add features to this new version. If you have code that is already running in the previous version of Z2Pack, or you cannot switch to Python 3.4 yet, here's the deal: I will **keep supporting** the last version of Z2Pack 1.X as long as there is any need for it. I have also changed the website such that old versions of the documentation are now available `here <http://z2pack.ethz.ch/doc/version.html>`_.

.. rubric :: And now for the good news

I strongly believe that the package has become easier to use. Many of the things that were an afterthought in the previous version, such as how to restart a calculation or calculating just a single line, are now built into the core of Z2Pack. As a result, some of the quirks of the previous version have been eliminated. In the following sections, I will highlight some of the more prominent improvements.

.. rubric :: New way of calculating the Wannier charge centers

.. rubric :: Tight-binding models on steroids

The previous version of Z2Pack contained a submodule for creating tight-binding models. This module has now matured and became its own package: `TBmodels <http://z2pack.ethz.ch/tbmodels>`_. Among other improvements, evaluating a tight-binding model is now orders of magnitude faster (I have yet to ca) 

.. rubric :: Saving results: going away from pickle


.. rubric :: Ideas for the future


