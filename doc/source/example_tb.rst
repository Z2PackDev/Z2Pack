An effective 2D model (tb)
==========================

In this example, we set up a tight-binding model for a quasi - 2D system. We consider 2 - sublattice square lattice with nearest-neighbour (inter-sublattice) and next - nearest - neighbour (intra-sublattice) interaction.

Using different parameters ``t1`` and ``t2`` and modifying the ``settings`` (currently they're the default values) can give you a feeling of the different parameters. Try setting ``num_strings`` very low (e.g. 3) and see how the convergence criteria will effect the result.

::

    import z2pack.tb as tb

    # Setting the interaction strength
    t1, t2 = (0.2, 0.3)

    # Settings used for wcc_calc. Feel free to play around with the different
    # options.
    settings = {
                'pos_tol': 1e-2,
                'gap_tol': 2e-2,
                'move_tol': 0.3,
                'iterator': range(8, 27, 2),
                'min_neighbour_dist': 1e-2,
                'use_pickle': True,
                'pickle_file': 'res_pickle.txt',
                'verbose': True
               }

    # Creating an empty Hamilton instance
    H = tb.Hamilton()

    # Creating the two atoms. The orbitals have opposite energies because
    # they are in different sublattices.
    H.add_atom(([1, 1], 1), [0, 0, 0])
    H.add_atom(([-1, -1], 1), [0.5, 0.5, 0])

    # Add hopping between different atoms
    # The first hopping is between the first orbital of the first atom and
    # the second orbital of the second atom, (inter-sublattice interation)
    H.add_hopping(((0, 0), (1, 1)),
                  tb.vectors.combine([0,-1],[0,-1],0),
                  t1,
                  phase = [1, -1j, 1j, -1])
    # The second interaction is also inter-sublattice, but with the other
    # two orbitals. The strength is the same, but the phase is conjugated.
    H.add_hopping(((0, 1), (1, 0)),
                  tb.vectors.combine([0,-1],[0,-1],0),
                  t1,
                  phase = [1, 1j, -1j, -1])

    # These are intra-sublattice interactions between neighbouring U.C.
    # Sublattice A has positive, sublattice B negative interaction strength
    H.add_hopping((((0, 0), (0, 0)),((0, 1), (0, 1))),
                  tb.vectors.neighbours([0,1]),
                  t2)
    H.add_hopping((((1, 1), (1, 1)),((1, 0), (1, 0))),
                  tb.vectors.neighbours([0,1]),
                  -t2)

    # Creating the System
    tb_system = tb.System(H)

    # Creating a surface with strings along ky at kz=0. kx will go from
    # 0 to 0.5
    tb_surface = tb_system.surface(lambda kx: [kx / 2., 0, 0], [0, 1, 0])

    # The settings given above are used for wcc_calc
    tb_surface.wcc_calc(**settings)
    tb_surface.plot()
    print('Z2 invariant: {2}'.format(tb_surface.invariant()))
