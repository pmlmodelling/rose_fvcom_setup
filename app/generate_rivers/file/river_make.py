import numpy as np
import pickle as pk
import netCDF4 as nc
import sys
import datetime as dt
import PyFVCOM as pf

import fvcom_river as fr

grid_name = sys.argv[1]
common_dir = sys.argv[2]
start_date = dt.datetime.strptime(sys.argv[3],'%Y-%m-%d_%H:%M:%S') - dt.timedelta(days=2) # Must start before FVCOM run
end_date = dt.datetime.strptime(sys.argv[4],'%Y-%m-%d_%H:%M:%S')
native_coordinates = sys.argv[5]
wrf_nc_file_str = sys.argv[6]


# Load the river model
with open('river_model.pk1','rb') as f:
    river_dict = pk.load(f)

river_list = []
for this_obj in river_dict.values():
    this_obj.mouth_lon = float(this_obj.mouth_lon)
    this_obj.mouth_lat = float(this_obj.mouth_lat)
    this_obj.salinity = 0
    river_list.append(this_obj)

# Add the new WRF data
forecast_nc = nc.Dataset(wrf_nc_file_str, 'r')

wrf_vars = ['RAINNC', 'T2', 'Times'] 
forecast_data = {}
for this_var in wrf_vars:
    forecast_data[this_var] = forecast_nc.variables[this_var][:]  

date_str_raw = [b''.join(this_date_raw) for this_date_raw in forecast_data['Times']]
forecast_data['times'] = np.asarray([dt.datetime.strptime(this_date_str.decode('utf-8'), '%Y-%m-%d_%H:%M:%S') for this_date_str in date_str_raw])

for this_river in river_list:
    if hasattr(this_river, 'wrf_catchment_factors'):
        this_rain = np.sum(np.sum(forecast_data['RAINNC']*this_river.wrf_catchment_factors, axis=2), axis=1)
        this_river.addToSeries('catchment_precipitation', this_rain, forecast_data['times'])
    
        this_temp = np.zeros(len(forecast_data['times']))
        for i in range(0, len(forecast_data['times'])):
            this_temp[i] = np.average(forecast_data['T2'][i,:,:], weights=this_river.wrf_catchment_factors)
        this_river.addToSeries('catchment_temp', this_temp, forecast_data['times'], override=True)

for this_river in river_list:
    try:
        this_river._expandDateSeries(start_date, end_date)
    except:
        pass

# Get and write out the forecast predictions
grid = common_dir + '/' + grid_name + '_grd.dat'
native_coordinates = 'cartesian'
obc_file = common_dir + '/' + grid_name + '_obc.dat'
output_file = grid_name + '_riv.nc'
output_file_nml = grid_name + '_riv.nml'

positions, names, times, flux_array, temperature, salinity, ersem_dict, sediment_dict = fr.get_pyfvcom_prep(river_list, start_date, end_date, ersem=False, noisy=True)

salinity = np.ones(salinity.shape)
flux_array[flux_array < 0] = 0

aqua_prep = pf.preproc.Model(start_date, end_date, grid, native_coordinates, zone='30N')
aqua_prep.add_open_boundaries(obc_file)
aqua_prep.add_rivers(positions, names, times, flux_array, temperature, salinity, threshold=np.inf, history='', info='')
aqua_prep.check_rivers(max_discharge=400, min_depth=None, open_boundary_proximity=None, noisy=False)
aqua_prep.write_river_forcing(output_file, ersem=False)
aqua_prep.write_river_namelist(output_file_nml, output_file, vertical_distribution='uniform')
