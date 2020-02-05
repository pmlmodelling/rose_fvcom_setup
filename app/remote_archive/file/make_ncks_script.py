import numpy as np
import datetime as dt
import sys

import PyFVCOM as pf

fvcom_output_path = sys.argv[1]
fvcom_grid_name = sys.argv[2]
start_date = dt.datetime.strptime(sys.argv[3], '%Y-%m-%d')
end_date = dt.datetime.strptime(sys.argv[4], '%Y-%m-%d') - dt.timedelta(days=1)

date_list = pf.utilities.time.date_range(start_date, end_date)

with open('make_daily_nc.sh', 'w') as f:
    f.write('#!/bin/bash \n')

this_filestr = '{}/{}_0001.nc'.format(fvcom_output_path,fvcom_grid_name)
this_fr = pf.read.FileReader(this_filestr)

for i, this_date in enumerate(date_list):
    time_ind = [np.argwhere(this_fr.time.datetime == this_date), np.argwhere(this_fr.time.datetime == this_date + dt.timedelta(hours=24))]

    this_out_filestr = '{}_{}.nc'.format(fvcom_grid_name, this_date.strftime('%Y-%m-%d'))
    with open('make_daily_nc.sh', 'a') as f:
        f.write('ncks -d time,{},{} {} {} \n'.format(np.squeeze(time_ind[0]), np.squeeze(time_ind[1]), this_filestr, this_out_filestr))    
