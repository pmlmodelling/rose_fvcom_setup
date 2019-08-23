import multiprocessing
import numpy as np
import datetime as dt
import glob as gb
import sys
from pathlib import Path

import PyFVCOM as pf
from PyFVCOM.utilities.time import date_range

cmems_data_dir = sys.argv[1]
start_date = dt.datetime.strptime(sys.argv[2], '%Y-%m-%d')
grid = sys.argv[3]
donor_filepath = sys.argv[4]

try:
    amm_7 = sys.argv[5]
except:
    amm_7 = False


"""
cmems_data_dir = '/data/sthenno1/scratch/modop/Data/CMEMS'
start_date = dt.datetime(2019,1,15)
grid = 'tamar_v2'
"""

cmems_time_res = 'hi'

if amm_7:
    fvcom_cmems_names = {'salinity':['SAL', 'vosaline'], 'temp':['TEM', 'votemper'],
    				        'v':['CUR', 'vomecrty'], 'u':['CUR', 'vozocrtx'],
					'zeta':['SSH', 'sossheig']}
else:
    fvcom_cmems_names = {'salinity':['SAL', 'so'], 'temp':['TEM', 'thetao'],
                                        'v':['CUR', 'vo'], 'u':['CUR', 'uo'],
                                        'zeta':['SSH', 'zos']}


# Modify a donor restart file.
restart = pf.preproc.Restart(donor_filepath,
                          variables=['siglay', 'siglev'])

# and alter the time variable
restart.time.datetime = np.asarray([start_date])
ref_date = dt.datetime(1858,11,17,0,0,0)
restart.time.time = np.asarray([(start_date - ref_date).days])
restart.time.Itime = np.asarray([(start_date - ref_date).days])
restart.time.Times = np.asarray(['{}T00:00:00.000000'.format(start_date.strftime('%Y-%m-%d'))])

restart.replaced.append('time')
restart.replaced.append('Itime')
restart.replaced.append('Times')


# We need to bracket the restart data in time with CMEMS data to ensure it interpolates properly.
for this_fvcom, this_var in fvcom_cmems_names.items():
    cmems_file_list = []
    offset = dt.timedelta(days=1)
    for this_date_dt in date_range(start_date - offset, start_date + offset):
        this_date = this_date_dt.strftime('%Y%m%d')
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

    # Interpolate onto the FVCOM grid.
    if this_fvcom in ['u', 'v']:
        this_mode = 'elements'
    elif this_fvcom == 'zeta':
        this_mode = 'surface'
    else:
        this_mode = 'nodes'

    restart.replace_variable_with_regular(this_fvcom, this_var[1], this_data_reader, constrain_coordinates=True, mode=this_mode)

for this_var in fvcom_cmems_names.keys():
    setattr(restart.data, this_var, getattr(restart.data,this_var)[np.newaxis,...])

# replace Times as need to be a 26 character array
restart.time.Times = np.asarray(list(restart.time.Times[0]))[np.newaxis,:]
restart.write_restart('{}_restart_0001.nc'.format(grid))

