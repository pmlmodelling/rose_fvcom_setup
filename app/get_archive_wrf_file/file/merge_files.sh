#!/bin/bash

# Script to merge the individual runs into month long chunks ready for
# conversion with wrf_to_fvcom.

module purge
module load nco

files=($(\ls raw_wrf_file*))

# Now convert to FVCOM forcing files. These files have all had their first
# time step removed as that's just the initial condition. So, you'd need to
# add a -dTime,1,, to the ncrcat command to drop the first time step if
# that's not been done. Once they're all converted, ncrcat them all
# together into a single file for this month.

n=0
for this_file in "${files[@]}"; do
	echo ${this_file}
	./wrf_to_fvcom_ceto -i ${this_file} -o wnd_file_${n}.nc -latitude 55.0
	ncks -d Time,1,8 wnd_file_${n}.nc wnd_file_trim_${n}.nc	
	rm ${this_file}
	rm wnd_file_${n}.nc
	((n++))
done

ncrcat -O -h $(\ls -1 wnd_file_trim*.nc | sort -u) wnd_file.nc
rm wnd_file_trim* || true
