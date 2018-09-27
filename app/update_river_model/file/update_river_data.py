import numpy as np
import datetime as dt
import glob as gb
import netCDF4 as nc
import pickle as pk
import sys

import fvcom_river as fr


wrf_forecast_out_dir = sys.argv[1]
end_date = dt.datetime.strptime(sys.argv[2],'%Y-%m-%d')

# Load the river model
with open('river_model.pk1','rb') as f:
	river_dict = pk.load(f)

start_date = end_date
for this_river in river_dict.values():
	this_river_update = np.max(this_river.catchment_precipitation[0])
	if this_river_update < start_date:
		start_date = this_river_update

if start_date == end_date:
	print('Already up to date')

else:	

	date_list = np.asarray([start_date + dt.timedelta(days=int(this_ind)) for this_ind in np.arange(0, (end_date - start_date).days + 1)])

	missing_dates = []

	for this_date in date_list:
		print(this_date)
		this_date_str = this_date.strftime('%Y%m%d')
		potential_files = gb.glob('{}/{}*_forecast/wrfout_d03*'.format(wrf_forecast_out_dir, this_date_str))
		try:
			this_wrf_nc = nc.Dataset(potential_files[-1], 'r')
			wrf_date_str_raw = this_wrf_nc.variables['Times'][:]
			wrf_date_str = np.asarray([b''.join(this_str) for this_str in wrf_date_str_raw])
			wrf_dt = np.asarray([dt.datetime.strptime(this_str.decode('utf-8'),'%Y-%m-%d_%H:%M:%S') for this_str in wrf_date_str])
			wrf_dt_date = np.asarray([this_dt.date() for this_dt in wrf_dt]) 

			date_match = wrf_dt_date == this_date.date()

			forecast_data = {'times': wrf_dt[date_match], 'RAINNC': this_wrf_nc.variables['RAINNC'][date_match,:,:], 
								'T2': this_wrf_nc.variables['T2'][date_match,:,:]}
			this_wrf_nc.close()
		 
			for this_river_name, this_river in river_dict.items():
				this_rain = np.sum(np.sum(forecast_data['RAINNC']*this_river.wrf_catchment_factors, axis=2), axis=1)
				this_river.addToSeries('catchment_precipitation', this_rain, forecast_data['times'], override=True)

				this_temp = np.zeros(len(forecast_data['times']))
				for i in range(0, len(forecast_data['times'])):
					this_temp[i] = np.average(forecast_data['T2'][i,:,:], weights=this_river.wrf_catchment_factors)
				this_river.addToSeries('catchment_temp', this_temp, forecast_data['times'], override=True)

		except:
			missing_dates.append(this_date)

	missing_dates_1 = []

	for this_date in missing_dates:
		print('Trying to fill for {}'.format(this_date))
		this_date_m1 = this_date - dt.timedelta(days=1)
		this_date_str = this_date_m1.strftime('%Y%m%d')
		potential_files = gb.glob('{}/{}*_forecast/wrfout_d03*'.format(wrf_forecast_out_dir, this_date_str))

		try:
			this_wrf_nc = nc.Dataset(potential_files[-1], 'r')
			wrf_date_str_raw = this_wrf_nc.variables['Times'][:]
			wrf_date_str = np.asarray([b''.join(this_str) for this_str in wrf_date_str_raw])
			wrf_dt = np.asarray([dt.datetime.strptime(this_str.decode('utf-8'),'%Y-%m-%d_%H:%M:%S') for this_str in wrf_date_str])
			wrf_dt_date = np.asarray([this_dt.date() for this_dt in wrf_dt]) 

			date_match = wrf_dt_date == this_date.date()

			forecast_data = {'times': wrf_dt[date_match], 'RAINNC': this_wrf_nc.variables['RAINNC'][date_match,:,:],
								'T2': this_wrf_nc.variables['T2'][date_match,:,:]}
			this_wrf_nc.close()

			for this_river_name, this_river in river_dict.items():
				this_rain = np.sum(np.sum(forecast_data['RAINNC']*this_river.wrf_catchment_factors, axis=2), axis=1)
				this_river.addToSeries('catchment_precipitation', this_rain, forecast_data['times'], override=True)

				this_temp = np.zeros(len(forecast_data['times']))
				for i in range(0, len(forecast_data['times'])):
					this_temp[i] = np.average(forecast_data['T2'][i,:,:], weights=this_river.wrf_catchment_factors)
				this_river.addToSeries('catchment_temp', this_temp, forecast_data['times'], override=True)

		except:
			missing_dates_1.append(this_date)

	missing_dates_2 = []
	for this_date in missing_dates_1:
		this_date_m1 = this_date - dt.timedelta(days=3)
		this_date_str = this_date_m1.strftime('%Y%m%d')
		potential_files = gb.glob('{}/{}*_forecast/wrfout_d03*'.format(wrf_forecast_out_dir, this_date_str))

		try:
			this_wrf_nc = nc.Dataset(potential_files[-1], 'r')
			wrf_date_str_raw = this_wrf_nc.variables['Times'][:]
			wrf_date_str = np.asarray([b''.join(this_str) for this_str in wrf_date_str_raw])
			wrf_dt = np.asarray([dt.datetime.strptime(this_str.decode('utf-8'),'%Y-%m-%d_%H:%M:%S') for this_str in wrf_date_str])
			wrf_dt_date = np.asarray([this_dt.date() for this_dt in wrf_dt])

			date_match = wrf_dt_date == this_date.date()

			forecast_data = {'times': wrf_dt[date_match], 'RAINNC': this_wrf_nc.variables['RAINNC'][date_match,:,:],
								'T2': this_wrf_nc.variables['T2'][date_match,:,:]}
			this_wrf_nc.close()

			for this_river_name, this_river in river_dict.items():
				this_rain = np.sum(np.sum(forecast_data['RAINNC']*this_river.wrf_catchment_factors, axis=2), axis=1)
				this_river.addToSeries('catchment_precipitation', this_rain, forecast_data['times'], override=True)

				this_temp = np.zeros(len(forecast_data['times']))
				for i in range(0, len(forecast_data['times'])):
					this_temp[i] = np.average(forecast_data['T2'][i,:,:], weights=this_river.wrf_catchment_factors)
				this_river.addToSeries('catchment_temp', this_temp, forecast_data['times'], override=True)

		except:
			missing_dates_2.append(this_date)

	missing_dates_3 = []
	for this_date in missing_dates_2:
		this_date_m1 = this_date - dt.timedelta(days=3)
		this_date_str = this_date_m1.strftime('%Y%m%d')
		potential_files = gb.glob('{}/{}*_forecast/wrfout_d03*'.format(wrf_forecast_out_dir, this_date_str))

		try:
			this_wrf_nc = nc.Dataset(potential_files[-1], 'r')
			wrf_date_str_raw = this_wrf_nc.variables['Times'][:]
			wrf_date_str = np.asarray([b''.join(this_str) for this_str in wrf_date_str_raw])
			wrf_dt = np.asarray([dt.datetime.strptime(this_str.decode('utf-8'),'%Y-%m-%d_%H:%M:%S') for this_str in wrf_date_str])
			wrf_dt_date = np.asarray([this_dt.date() for this_dt in wrf_dt])

			date_match = wrf_dt_date == this_date.date()

			forecast_data = {'times': wrf_dt[date_match], 'RAINNC': this_wrf_nc.variables['RAINNC'][date_match,:,:],
								'T2': this_wrf_nc.variables['T2'][date_match,:,:]}
			this_wrf_nc.close()

			for this_river_name, this_river in river_dict.items():
				this_rain = np.sum(np.sum(forecast_data['RAINNC']*this_river.wrf_catchment_factors, axis=2), axis=1)
				this_river.addToSeries('catchment_precipitation', this_rain, forecast_data['times'], override=True)

				this_temp = np.zeros(len(forecast_data['times']))
				for i in range(0, len(forecast_data['times'])):
					this_temp[i] = np.average(forecast_data['T2'][i,:,:], weights=this_river.wrf_catchment_factors)
				this_river.addToSeries('catchment_temp', this_temp, forecast_data['times'], override=True)

		except:
			missing_dates_3.append(this_date)

	for this_date in missing_dates_3:
		this_date_m1 = this_date - dt.timedelta(days=4)
		this_date_str = this_date_m1.strftime('%Y%m%d')
		potential_files = gb.glob('{}/{}*_forecast/wrfout_d03*'.format(wrf_forecast_out_dir, this_date_str))

		try:
			this_wrf_nc = nc.Dataset(potential_files[-1], 'r')
			wrf_date_str_raw = this_wrf_nc.variables['Times'][:]
			wrf_date_str = np.asarray([b''.join(this_str) for this_str in wrf_date_str_raw])
			wrf_dt = np.asarray([dt.datetime.strptime(this_str.decode('utf-8'),'%Y-%m-%d_%H:%M:%S') for this_str in wrf_date_str])
			wrf_dt_date = np.asarray([this_dt.date() for this_dt in wrf_dt])

			date_match = wrf_dt_date == this_date.date()

			forecast_data = {'times': wrf_dt[date_match], 'RAINNC': this_wrf_nc.variables['RAINNC'][date_match,:,:],
								'T2': this_wrf_nc.variables['T2'][date_match,:,:]}
			this_wrf_nc.close()

			for this_river_name, this_river in river_dict.items():
				this_rain = np.sum(np.sum(forecast_data['RAINNC']*this_river.wrf_catchment_factors, axis=2), axis=1)
				this_river.addToSeries('catchment_precipitation', this_rain, forecast_data['times'], override=True)

				this_temp = np.zeros(len(forecast_data['times']))
				for i in range(0, len(forecast_data['times'])):
					this_temp[i] = np.average(forecast_data['T2'][i,:,:], weights=this_river.wrf_catchment_factors)
				this_river.addToSeries('catchment_temp', this_temp, forecast_data['times'], override=True)

		except:
			print('Giving up on {}'.format(this_date))

	with open('river_model.pk1','wb') as f:
		pk.dump(river_dict, f, pk.HIGHEST_PROTOCOL)


