import numpy as np
import datetime as dt
import glob as gb
import netCDF4 as nc
import pickle as pk
import sys

import fvcom_river as fr


wrf_forecast_out_dir = sys.argv[1]
wrf_forecast_out_dir_strfmt = sys.argv[2]
end_date = dt.datetime.strptime(sys.argv[3],'%Y-%m-%d')
no_miss_loops = 4

# Load the river model
with open('river_model.pk1','rb') as f:
    river_dict = pk.load(f)

start_date = end_date
for this_river in river_dict.values():
    if hasattr(this_river, 'catchment_precipitation'):
        this_river_update = np.max(this_river.catchment_precipitation[0])
        if this_river_update < start_date:
            start_date = this_river_update


if start_date == end_date:
    print('Already up to date')

else:    

    missing_dates = np.asarray([start_date + dt.timedelta(days=int(this_ind)) for this_ind in np.arange(0, (end_date - start_date).days + 1)])

    for this_missing_loop in np.arange(-1, no_miss_loops):
        new_missing_dates = []
        for this_date in missing_dates:
            if this_missing_loop >= 0:
                print('Trying again to fill for {}'.format(this_date))
            else:
                print(this_date)
            this_date_m1 = this_date - dt.timedelta(days=int(this_missing_loop))
            this_date_str = this_date_m1.strftime(wrf_forecast_out_dir_strfmt)
            potential_files = gb.glob('{}/*{}*/wrfout_d03*'.format(wrf_forecast_out_dir, this_date_str))

            try:
                this_wrf_nc = nc.Dataset(potential_files[-1], 'r')
                wrf_date_str_raw = this_wrf_nc.variables['Times'][:]
                wrf_date_str = np.asarray([b''.join(this_str) for this_str in wrf_date_str_raw])
                wrf_dt = np.asarray([dt.datetime.strptime(this_str.decode('utf-8'),'%Y-%m-%d_%H:%M:%S') for this_str in wrf_date_str])
                wrf_dt_date = np.asarray([this_dt.date() for this_dt in wrf_dt]) 

                date_match = wrf_dt_date == this_date.date()
                first_date_ind = np.min(np.where(date_match))
                last_date_ind = np.max(np.where(date_match)) + 1
                
                if first_date_ind > 0:
                    rain_diff = this_wrf_nc.variables['RAINNC'][:][first_date_ind:last_date_ind,:,:]- this_wrf_nc.variables['RAINNC'][:][first_date_ind-1:last_date_ind-1,:,:]
                else:
                    rain_diff_part = this_wrf_nc.variables['RAINNC'][:][first_date_ind+1:last_date_ind,:,:]- this_wrf_nc.variables['RAINNC'][:][first_date_ind:last_date_ind-1,:,:]
                    rain_diff = np.vstack([this_wrf_nc.variables['RAINNC'][:][first_date_ind,:,:][np.newaxis,:,:], rain_diff_part]) 

                forecast_data = {'times': wrf_dt[date_match], 'RAINNC': rain_diff,
                                    'T2': this_wrf_nc.variables['T2'][date_match,:,:]}
                this_wrf_nc.close()

                for this_river_name, this_river in river_dict.items():
                    if hasattr(this_river, 'addToSeries'):
                        this_rain = np.sum(np.sum(forecast_data['RAINNC']*this_river.wrf_catchment_factors, axis=2), axis=1)
                        this_river.addToSeries('catchment_precipitation', this_rain, forecast_data['times'], override=True)

                        this_temp = np.zeros(len(forecast_data['times']))
                        for i in range(0, len(forecast_data['times'])):
                            this_temp[i] = np.average(forecast_data['T2'][i,:,:], weights=this_river.wrf_catchment_factors)
                        this_river.addToSeries('catchment_temp', this_temp, forecast_data['times'], override=True)
                        if hasattr(this_river, 'river_obj'):
                            this_river.catchment_precipitation = this_river.river_obj.catchment_precipitation
            except:
                new_missing_dates.append(this_date)
            missing_dates = new_missing_dates[:] 

    with open('river_model.pk1','wb') as f:
        pk.dump(river_dict, f, pk.HIGHEST_PROTOCOL)


