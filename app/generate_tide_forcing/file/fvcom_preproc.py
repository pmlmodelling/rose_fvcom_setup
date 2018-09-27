from datetime import datetime
import PyFVCOM as pf
import sys

casename = sys.argv[1]
start_str = sys.argv[2]
end_str = sys.argv[3]

# Define a start, end and sampling interval for the tidal data
start = datetime.strptime(start_str, '%Y-%m-%d')
end = datetime.strptime(end_str, '%Y-%m-%d')
interval = 1 / 24  # 1 hourly in units of days
model = pf.preproc.Model(start, end, 'tamar_v2_grd.dat', sampling=interval,
                         native_coordinates='cartesian', zone='30U', noisy=True)

# Define everything we need for the open boundaries.

# We need the TPXO data to predict tides at the boundary. Get that from here:
#    ftp://ftp.oce.orst.edu/dist/tides/Global/tpxo9_netcdf.tar.gz
# and extract its contents in the PyFVCOM/examples directory.
fvcom_harmonics = 'tamar_2006_harmonics.nc'
constituents = ['M2', 'S2']
for boundary in model.open_boundaries:
    # Create a 5km sponge layer for all open boundaries.
    #boundary.add_sponge_layer(5000, 0.001)
    # Set the type of open boundary we've got.
    boundary.add_type(1)  # prescribed surface elevation
    # And add some tidal data.
    boundary.add_fvcom_tides(fvcom_harmonics, predict='zeta', constituents=constituents, interval=interval, serial=True)

# Make a vertical grid with 21 uniform levels
model.sigma.type = 'uniform'
model.dims.levels = 24

# Write out the files for FVCOM.
model.write_grid('{}_grd.dat'.format(casename), depth_file='{}_dep.dat'.format(casename))
#model.write_sponge('operational_spg.dat')
model.write_coriolis('{}_cor.dat'.format(casename))
model.write_sigma('{}_sigma.dat'.format(casename))
model.write_tides('{}_elevtide.nc'.format(casename))

