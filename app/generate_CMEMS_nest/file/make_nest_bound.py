import numpy as np
import netCDF4 as nc
import datetime as dt
import glob as gb
import sys

import PyFVCOM as pf

"""
cmems_data_dir = '/data/sthenno1/scratch/modop/Data/CMEMS'
start_date = dt.datetime(2019,4,30)
end_date = dt.datetime(2019,5,2)
grid = 'tamar_v2_grd.dat'
sigma_file = 'sigma_gen.dat'
native_coordinates = 'cartesian'
fvcom_harmonics = '/data/sthenno1/backup/mbe/Data/harmonics_files/tamar_2006_harmonics.nc'
interval = 1/24 

"""

cmems_data_dir = sys.argv[1]
start_date = dt.datetime.strptime(sys.argv[2], '%Y-%m-%d')
end_date = dt.datetime.strptime(sys.argv[3], '%Y-%m-%d')
grid = sys.argv[4]
sigma_file = sys.argv[5]
native_coordinates = sys.argv[6]
fvcom_harmonics = sys.argv[7]
interval = 1/float(sys.argv[8])
adjust_tides = sys.argv[9].split(',')
no_nests = int(sys.argv[10])
try:
    amm_7 = sys.argv[11]
except:
    amm_7 = False

constituents = ['M2', 'S2']
output_file = 'boundary_nest.nc'.format(grid)
cmems_time_res = 'hi'

if 'None' in adjust_tides:
    adjust_tides = []

##############################################################################################
# Setup preproc Model object
aqua_prep = pf.preproc.Model(start_date, end_date, grid, native_coordinates, zone='30N', sampling=interval)
aqua_prep.add_sigma_coordinates(sigma_file)

# Make the nested boundary object
aqua_prep.add_nests(no_nests)
aqua_prep.add_nests_harmonics(fvcom_harmonics, harmonics_vars=['u', 'v', 'ua', 'va', 'zeta'], constituents=constituents, pool_size=20)

# Make the regular readers for the CMEMS data
if amm_7:
    fvcom_cmems_names = {'salinity':['SAL', 'vosaline'], 'temp':['TEM', 'votemper'],
					'v':['CUR', 'vomecrty'], 'u':['CUR', 'vozocrtx'],
					'zeta':['SSH', 'sossheig']}
else:
    fvcom_cmems_names = {'salinity':['SAL', 'so'], 'temp':['TEM', 'thetao'],
                                        'v':['CUR', 'vo'], 'u':['CUR', 'uo'],
                                        'zeta':['SSH', 'zos']}

dt_list = [start_date + dt.timedelta(days = int(i)) for i in np.arange(-1, (end_date - start_date).days + 2)]
datestr_list = [this_date.strftime('%Y%m%d') for this_date in dt_list]

for this_fvcom, this_var in fvcom_cmems_names.items():
	cmems_file_list = []
	for this_date in datestr_list:
		if this_var[0] == 'SSH':
			poss_files = gb.glob('{}/*{}*{}*/*{}.nc'.format(cmems_data_dir, 'hi', this_var[0], this_date))
		else:
			poss_files = gb.glob('{}/*{}*{}*/*{}.nc'.format(cmems_data_dir, cmems_time_res, this_var[0], this_date))
		# Handle that sometimes theres multiple files for one day from different forecast runs
		if len(poss_files) > 1:
			chosen_file = poss_files[0]
			for this_file in poss_files[1:]:
				if this_file > chosen_file:
					chosen_file = this_file
			cmems_file_list.append(chosen_file)
		elif len(poss_files) == 1:
			cmems_file_list.append(poss_files[0])

	if this_var[0] =='SSH':
		reg_reader = pf.preproc.Regular2DReader
	else:
		reg_reader = pf.preproc.RegularReader

	this_data_reader = reg_reader(cmems_file_list[0], [this_var[1]])

	if len(cmems_file_list) > 1:
		for this_file in cmems_file_list[1:]:
			this_data_reader = reg_reader(this_file, [this_var[1]]) >> this_data_reader

	aqua_prep.add_nests_regular(this_fvcom, this_data_reader, this_var[1], constrain_coordinates=True)

# Depth avg the velocities
aqua_prep.avg_nest_force_vel()

# Write the forcing file 
aqua_prep.write_nested_forcing(output_file, adjust_tides=adjust_tides)
