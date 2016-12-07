.. _z2pack_developers:

Developer's Guide
=================

This guide is meant for people who wish to contribute to the development of Z2Pack. First of all, let me say that I really appreciate all contributions! If you ever get stuck or wonder how to best do something, please don't hesitate to contact `me <greschd@gmx.ch>`_ directly. Also, the developer's guide is a work in progress. If you have any questions or suggestions, please let me know.

Coding style
------------
For the design of the code, the main goal is to make the user interface as simple as possible. While simplicity of the internal structure should obviously not be ignored, the public interface takes precedence.

In terms of formatting, please adhere to the `PEP 8 style <https://www.python.org/dev/peps/pep-0008/>`_. I'd recommend using a tool like `autopep8 <https://pypi.python.org/pypi/autopep8>`_ for this purpose. Furthermore, I recommend using `pylint <https://www.pylint.org/>`_ for a more thorough check of the code quality. Be aware, however, that pylint is often overzealous -- use your best judgement here.

All code must be tested. You can use the **pytest-cov** tool to see the code coverage. Documentation has to be provided for everything in the public interface.

Code structure
--------------
If you're contributing to Z2Pack, I'll assume you are already somewhat familiar with the public interface (as described in the Tutorial and Reference). Here, I'll explain some of the internals and concepts behind the code. The focus is on things that might not be obvious at first glance from looking at the source code.

.. toctree::
    :maxdepth: 2
    
    devguide_data_result.rst
    devguide_control.rst
    devguide_io.rst
    
