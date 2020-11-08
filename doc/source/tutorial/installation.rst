.. _z2pack_tutorial_installation :

Installation and Setup
======================

Installing Z2Pack
-----------------

The basic installation of Z2Pack should usually be quite straightforward. Just make sure you have a Python interpreter which is at least version 3.4, and install it by typing

.. code :: bash

    python -m pip install --user z2pack

in your console.

.. note ::

    Depending on your system, the command to call the Python interpreter may be either ``python`` or ``python3``. In this tutorial, I will just refer to it as ``python``. There are also other ways to invoke ``pip``, but the above should work on all platforms.

You can check that this worked by firing up your Python interpreter and trying to import z2pack (all lowercase). The result should be something like this:

.. code :: python

    greschd@laptopdg:~$ python
    Python 3.5.1+ (default, Mar 30 2016, 22:46:26)
    [GCC 5.3.1 20160330] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import z2pack
    >>> z2pack.__version__
    '2.1.0'
    >>>

Unless you want some additional information, you can now skip ahead to the parts where I explain how to set up Z2Pack with :ref:`tight-binding models <setup_tight_binding>` or :ref:`first-principles codes <setup_first_principles>`. If you don't need that, you can go straight to the section on :ref:`creating a System <z2pack_tutorial_system>`.

.. note ::

    A cool way to install things in Python without "polluting" your system is to use `virtual environments <https://docs.python.org/3/library/venv.html>`_. To help you manage your virtual environments, the `virtualenvwrapper <https://pypi.python.org/pypi/virtualenvwrapper>`_ tool works great. Virtual environments can also be used to install packages even if you don't have administrator access on your system. When installing Z2Pack in a virtual environment, the ``--user`` argument must be omitted.

If you want to install Z2Pack from source, you can download the code either from GitHub_ (development version) or PyPI_ (release version). You can then install it by again using ``pip``

.. code :: bash

    python -m pip install --user path_to_z2pack

where ``path_to_z2pack`` should be the path to the top folder of the downloaded files. If you prefer not to install anything, you could also just remember to always put the following at the top of your scripts:

.. code :: python

    import sys
    sys.path.append('path_to_z2pack')
    import z2pack

.. _setup_tight_binding :

Installing the tight-binding backend
------------------------------------

For calculating tight-binding models, Z2Pack uses the `TBmodels <http://tbmodels.greschd.ch>`_ package. It is installed in the same way as Z2Pack:

.. code :: bash

    python -m pip install --user tbmodels

Again, you can check that this worked by running the interpreter:

.. code :: python

    greschd@laptopdg:~$ python
    Python 3.5.1+ (default, Mar 30 2016, 22:46:26)
    [GCC 5.3.1 20160330] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import tbmodels
    >>> tbmodels.__version__
    '1.1.0'
    >>>

.. _setup_first_principles :

Setting up first-principles codes
---------------------------------

Z2Pack uses the Wannier90 software to compute overlap matrices from first-principles. This means that Z2Pack can be used with any first - principles code that interfaces to Wannier90. If you are using Wannier90 **version 2.1.0** or higher, it is compatible with Z2Pack.

For first-principles codes that are not yet compatible with Wannier90 2.1, a modified version of Wannier90 1.2 and 2.0 is available here:

:download:`Wannier90 1.2, modified for ABINIT<../downloads/wannier90-1.2.0.1.tar.gz>`
:download:`Wannier90 1.2<../downloads/wannier90-1.2.tar.gz>`
:download:`Wannier90 2.0<../downloads/wannier90-2.0.0.tar.gz>`

.. warning:: Compiling your first-principles code with this version of Wannier90 will likely break Wannier90 for purposes other than Z2Pack. It is recommended to create a separate instance of the first-principles code for Z2Pack.

ABINIT Setup
~~~~~~~~~~~~
The following is a guide on how to install ABINIT with the modified Wannier90 source by replacing the Wannier90 fallback in ABINIT. If your usual routine is to install ABINIT with Wannier90 as an external (pre-compiled) library, it may be easier to compile the modified Wannier90 source again and then linking to that.

* Download the modified Wannier90 source and copy it to the ``tarballs`` directory of ABINIT (usually ``~/.abinit/tarballs``)
* Now we need to change the checksum ABINIT expects from the Wannier90 source.

  * Get the md5sum for both the original (un-modified) Wannier90 source
    and the modified source with the command ``md5sum filename``.
  * Go to your ABINIT source folder and open the file ``fallbacks/configure``. Search and replace every instance of the old checksum with the new one. You should find 2 checksums to replace.

* Build ABINIT with Wannier90 enabled. If one of the previous steps were not done correctly, the installation will likely get stuck trying to download Wannier90.

VASP Setup
~~~~~~~~~~
For VASP, the installation routine doesn't differ from installing VASP with a regular version of Wannier90. Compile the modified Wannier90 source and link to it when installing VASP.

.. _GitHub: http://github.com/Z2PackDev/Z2Pack
.. _PyPI: https://pypi.python.org/pypi/z2pack
