.. _z2pack_tutorial_plot :

Plotting
========

To help you plot your results, Z2Pack contains a few convenience functions in the :mod:`z2pack.plot` submodule. 

* :func:`z2pack.plot.wcc` plots the WCC and (optionally) their largest gap.
* :func:`z2pack.plot.chern` plots the sum of WCC (polarization).
* :func:`z2pack.plot.wcc_symmetry` plots the WCC and their largest gap. The WCC are colored according to the expectation value of a given operator.

The simplest way of using these plotting functions is by just passing them a surface result.

.. code :: python

    import z2pack
    import matplotlib.pyplot as plt
    
    result = ...
    z2pack.plot.wcc(result)
    plt.show()

Because Z2Pack uses :py:mod:`matplotlib<matplotlib.pyplot>` to create the plots, ``plt.show()`` will show the plot on screen.

To get more control over how the plot looks, you can also create the figure and axis yourself and then pass the ``axis`` as a keyword argument.

.. code :: python

    result = ...
    fig, ax = plt.subplots()
    z2pack.plot.wcc(result, axis=ax)
    # modify the axis labels etc.
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['a', 'b'])
    plt.savefig('path_to_figure.pdf')
    
The same technique can be used to combine multiple plots into one figure.

Finally, there are keyword arguments (named ``settings``, ``wcc_settings`` or ``gap_settings``) which are passed to the :py:mod:`matplotlib` function creating the plot. They can be changed to modify the appearance of the different markers. Please consult the :ref:`reference <plot>` to see the default values for these. The following example shows how to change the color of the markers and lines in :func:`z2pack.plot.chern` from red to blue.

.. code :: python
    
    result = ...
    z2pack.plot.chern(
        result,
        settings=dict(
            marker='o',
            color='b',
            markerfacecolor='b'
        )
    )

