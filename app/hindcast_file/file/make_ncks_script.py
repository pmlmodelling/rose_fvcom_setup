import numpy as np
import datetime as dt
import sys

import PyFVCOM as pf

file_to_archive = sys.argv[1]
fvcom_grid_name = sys.argv[2]
archive_dir = sys.argv[3]
hindcast_days = int(sys.argv[4])

with open('make_daily_nc.sh', 'w') as f:
    f.write('#!/bin/bash \n')

this_fr = pf.read.FileReader(file_to_archive)
first_date = this_fr.time.datetime[0]

time_ind = [0, np.argwhere(this_fr.time.datetime == this_fr.time.datetime[0] + dt.timedelta(hours=(24*hindcast_days)-1))]

this_out_filestr = '{}_{}.nc'.format(fvcom_grid_name, this_fr.time.datetime[0].strftime('%Y-%m-%d'))
this_archive_filestr = '{}/{}'.format(archive_dir, this_out_filestr)

with open('make_daily_nc.sh', 'a') as f:
    f.write('ncks -d time,{},{} {} temp.nc \n'.format(np.squeeze(time_ind[0]), np.squeeze(time_ind[1]), file_to_archive))
    f.write('ncks --ppc default=4 temp.nc {} \n'.format(this_out_filestr))
    f.write('mv {} {}\n'.format(this_out_filestr, this_archive_filestr))
    f.write('rm temp.nc \n')








