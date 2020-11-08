# Contributing to Z2Pack

First off, thank you for considering to contribute to Z2Pack. Your contribution helps make Z2Pack better, and is greatly appreciated.

## Submitting issues

You should submit an issue on GitHub if you

* found a bug in the code
* have an idea for a new feature

If you found a bug, please make sure to include as much information about the bug as possible. It's always a good idea to describe what you were trying to do, which version of the code you were using, and to include either a traceback of the error, or a simple example demonstrating the issue.

However, don't worry about it if you don't know how to find any of this information -- an incomplete issue is better than no issue at all.

Please do not use the GitHub issues for general support questions. For this purpose, you can write to the [mailing list](mailto:z2pack@lists.phys.ethz.ch) instead. There is also an [archive](https://lists.phys.ethz.ch/pipermail/z2pack/) of the mailing list available.

## Writing documentation

An important way in which new users can contribute is by writing or improving the documentation. As somebody who is new to the project, it is easier to spot part of the documentation which might be unclear or incomplete. The documentation is built using [Sphinx](http://www.sphinx-doc.org/) which uses the [reStructuredText](http://docutils.sourceforge.net/rst.html) markup language. If all you want to do is edit some text, it shouldn't require detailed knowledge of the markup syntax, though: Just find the right spot in the documentation source (``.rst`` files) and edit it.

To build the documentation locally, you first need to pull the Z2Pack source, and install it (preferrably in a virtualenv) with

    pip install -e path_to_z2pack_source[dev]

where ``path_to_z2pack_source`` needs to be replaced with the top-level path of the Z2Pack source. In the ``doc`` subfolder, copy the configuration template ``config.mk.tpl`` to ``config.mk``. After that, you can simply call ``make`` to build and ``make view`` to open the documentation.

To contribute your changes to the documentation, you can commit them to your fork of the Z2Pack repository, and create a pull request on the main repository. The guidelines described in the next section about branching and pull requests also apply here.

Of course, improvements to documents outside the documentation, such such as this contributing guide, are also greatly appreciated.

## Contributing to the code

If you would like to contribute to the code itself, please have a look at the [developer's guide](https://z2pack.greschd.ch/en/latest/devguide/). Before you start working on something, it's usually a good idea to submit an issue describing what you're trying to do. That way, you can get feedback on how to solve the issue before starting to code.

New features should be added by branching off from the latest development branch (``dev/current``). Once you've started working on something, you can create a pull request if you would like to have some feedback on the code. You can put ``[WIP]`` (work in progress) in the PR title to let us know if you're still working on the code. To simplify the review and merging of pull requests, it is good practice to add only one feature in each PR. This is not a strict rule however -- use your best judgment to determine whether a set of changes are a logical unit.
