import z2pack
import sisl
import numpy as np
import matplotlib.pyplot as plt

# Read geometry, Hamiltonian and overlap matrix from SIESTA output using sisl
sile = sisl.get_sile('Bi2D_BHex.fdf')
geom = sile.read_geometry()
H = sile.read_hamiltonian(geometry=geom)

# Create two helper functions to retrieve Hamiltonian and overlap for arbitrary k points
Hk = lambda k: H.Hk(k=k, dtype=np.complex64, format='array')
Sk = lambda k: H.Sk(k=k, dtype=np.complex64, format='array')

# Create array with the position of all orbitals
pos = geom.fxyz[list(map(geom.o2a, np.arange(H.no)))]
# In non-collinear/spin-orbit calculations each orbital is repeated twice once with up and once with down spin
pos = np.repeat(pos, 2, axis=0)

# Create system in z2pack
system = z2pack.hm.System(
    hamilton=Hk,
    hermitian_tol=1e-5,
    basis_overlap=Sk,
    pos=pos,
    bands=30,
)

surface = lambda s, t: [t, s / 2, 0]

# Run the WCC calculations
settings = {
    'num_lines': 11,
    'pos_tol': 1e-2,
    'gap_tol': 2e-2,
    'move_tol': 0.3,
    'iterator': range(8, 27, 2),
    'min_neighbour_dist': 1e-2,
    'load': False,
}

result = z2pack.surface.run(
    system=system, surface=surface, save_file='./res.json', **settings
)

print('Z2 invariant:', z2pack.invariant.z2(result))

# Plot Wannier charge centers
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
wcc_settings = {
    's': 50.,
    'lw': 1.,
    'facecolor': 'none',
    'edgecolors': 'k',
    'label': 'HWCC'
}
gap_settings = {
    'marker': 'D',
    'color': 'b',
    'linestyle': '--',
    'label': 'Gap position'
}

z2pack.plot.wcc(
    result, axis=ax, wcc_settings=wcc_settings, gap_settings=gap_settings
)
ax.set_title('Bands 29, 30', fontsize=14)
ax.set_ylabel(r'$\bar{x} [a_x]$', fontsize=14)
ax.set_xlabel(r'$k_y [\pi/a_y]$', fontsize=14)
handles, labels = fig.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys())
plt.savefig('Bi2D_BHex.png')
