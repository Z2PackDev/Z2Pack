import z2pack
import sisl
import numpy as np
import matplotlib.pyplot as plt

# Read geometry, Hamiltonian and overlap matrix from SIESTA output using sisl
sile = sisl.get_sile('in.fdf')
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
nEl = 0 # number of electrons (grep 'number of electrons' out.fdf)
system = z2pack.hm.System(
    hamilton=Hk,
    basis_overlap=Sk,
    pos=pos,
    bands=nEl, 
)

surface = lambda s, t: [t, s / 2, 0]

# Run the WCC calculations
settings = {
# ...
}

result = z2pack.surface.run(
    system=system, surface=surface, **settings
)
