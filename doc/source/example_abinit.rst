A first-principles calculation with ABINIT
==========================================
The following is a very basic calculation of Z2 invariants using **ABINIT**
for a **generic system**. Before running this calculation, an SCF run is
required to create a density input file.

Because this file will be quite
large, it is recommended not to reference it in ``input_files`` (the first
variable to :class:`.fp.System`), but instead reference to it directly in
the ``.files`` file. This will avoid unnecessary copying.

The input files should be the same as for any NSCF run, except they should
not contain any k-point information and must include a call to Wannier90.
The Wannier90 input file should contain ``shell_list 1`` and use ``exclude_bands``
to exclude non-occupied bands.

Note also that you will have to **change the command** that is used to call
ABINIT to match your system.

.. code:: python

    import z2pack

    import matplotlib.pyplot as plt

    # Creating the System. Note that the SCF charge file does not need to be
    # copied, but instead can be referenced in the .files file.
    # The k-points input is appended to the .in file
    # The command (mpirun ...) will have to be replaced to match your system.
    system = z2pack.fp.System(["system_nscf.files", "system_nscf.in", "wannier90.win" ],
                              z2pack.fp.kpts.abinit,
                              "system_nscf.in",
                              "mpirun ~/software/abinit-7.8.2/src/98_main/abinit < " +
                              "system_nscf.files >& log"
                        )
        

    # Creating two surfaces, both with the pumping parameter t changing
    # ky from 0 to 0.5, and strings along kz.
    # The first plane is at kx = 0, the second one at kx = 0.5
    # Notice the different values of pickle_file to avoid overwriting the data.
    surface_0 = system.surface(lambda t: [0, t / 2, 0], [0, 0, 1],
                               pickle_file = './results/res_0.txt')
    surface_1 = system.surface(lambda t: [0.5, t / 2, 0], [0, 0, 1],
                               pickle_file = './results/res_1.txt')

    # WCC calculation - standard settings
    surface_0.wcc_calc()    
    surface_1.wcc_calc()

    # Combining the two plots
    fig, ax = plt.subplots(1, 2, sharey=True, figsize = (9,5))
    surface_0.plot(show=False, axis=ax[0])
    surface_1.plot(show=False, axis=ax[1])
    plt.savefig('plot.pdf', bbox_inches = 'tight')

    print('Z2 topological invariant at kx = 0: {0}'.format(surface_0.invariant()))
    print('Z2 topological invariant at kx = 0.5: {0}'.format(surface_1.invariant()))
