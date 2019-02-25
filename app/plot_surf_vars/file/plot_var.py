import matplotlib as mpl
mpl.use('Agg')

import sys
import multiprocessing
import numpy as np
from cmocean import cm

import PyFVCOM as pf
import pmltools as pt

labels = {'q2': 'Turbulent kinetic energy $(m^{2}s^{-2})$',
          'l': 'Turbulent macroscale $(m^{3}s^{-2})$',
          'q2l': 'Turbulent kinetic\nenergy x turblent\nmacroscale ($cm^{3}s^{-2}$)',
          'tke': 'Turbulent kinetic energy $(m^{2}s^{-2})$',
          'viscofh': 'Horizontal Turbulent Eddy Viscosity $(m^{2}s^{-1})$',
          'teps': 'Turbulent kinetic\nenergy x turblent\nmacroscale ($cm^{3}s^{-2}$)',
          'tauc': 'Bed shear stress $(m^{2}s^{-2})$',
          'temp': 'Temperature ($\degree C$)',
          'salinity': 'Salinity (PSU)',
          'zeta': 'Surface elevation (m)',
          'uv': 'Speed $(ms^{-1})$',
          'uava': 'Depth averaged speed $(ms^{-1})$',
          'uvanomaly': 'Speed anomaly $(ms^{-1})$',
          'direction': 'Direction $(\degree)$',
          'O3_c': 'Carbonate total dissolved\ninorganic carbon $(mmol C/m^3)$',
          'O3_pH': 'Carbonate pH',
          'O3_TA': 'Total alkalinity $(umol/kg)$',
          'O3_fair': 'Carbonate air-sea flux of $CO_{2} (mmol C/m^{2}/d)$',
          'volume': 'Node-based control water column volume $(m^{3})$'}

def plot_var(idx):
    plot = pf.plot.Plotter(fvcom, figsize=(23, 18), cmap=cmap, cb_label=label, extend=extension, res=None)

    plot.plot_field(np.squeeze(getattr(fvcom.data, var))[idx, level, :])
    plot.tripcolor_plot.set_clim(clim[0], clim[1])

    plot.axes.set_title(fvcom.time.Times[idx][:-7].replace('T', ' '))
    suffix = ''

    plot.figure.savefig('{}_{:04d}.png'.format(var, idx + 1),
                        bbox_inches='tight',
                        pad_inches=0.2,
                        dpi=120)
    plot.close()

fname = sys.argv[1]
var = sys.argv[2]
clim = [float(sys.argv[3]), float(sys.argv[4])]

print(fname)

cmap = pt.plotting.pmlcmaps(var)
pool_size = 4

fvcom = pf.read.FileReader(fname, [var]) 
label = labels[var]
extension = pt.plotting.colourbar_extension(*clim, getattr(fvcom.data, var).min(), getattr(fvcom.data, var).max())
level = 0


time_indices = range(fvcom.dims.time)
# Launch the parallel plotting and then close the pool ready for the
# next variable.
pool = multiprocessing.Pool(pool_size)
pool.map(plot_var, time_indices)
pool.close()



