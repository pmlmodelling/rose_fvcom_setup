#!/bin/bash --login

set -eu

# Get today's forecast data from CMEMS for the NW Shelf domain. Delete yesterday's whilst we're at it.

# CMEMS FTP username and password are stored in ~/.netrc to make this more secure.
forecast_days=$1
today=${today:-$(date +%Y%m%d)}
for day in $(seq -2 $forecast_days); do
    end=$(date +%Y%m%d -d "$today + $day days")
    echo -n "Getting forecast $today-$end "
    for var in CUR SAL SSH TEM; do
        dir=MetO-NWS-PHYS-hi-${var}
        if [ ! -d $dir ]; then
            mkdir $dir
        fi
        file=metoffice_foam1_amm7_NWS_${var}_b${today}_hi${end}.nc
        # Don't fail if we didn't get the file. This might just mean we're doing a hindcast download.
        #wget -qc ftp://nrt.cmems-du.eu/Core/NORTHWESTSHELF_ANALYSIS_FORECAST_PHYS_004_001_b/$dir/$file -O$dir/$file || true
		wget -c ftp://nrt.cmems-du.eu/Core/NORTHWESTSHELF_ANALYSIS_FORECAST_PHYS_004_001_b/$dir/$file -O$dir/$file
        # If we're doing a hindcast download we might end up with an empty file, so nuke it here.
        if [ ! -s $dir/$file ]; then
            rm $dir/$file
        fi
    done
    echo "done."
done

# Clear out the old forecast data.
yesterday=$(date +%Y%m%d -d "$today - 1 day")
for day in $(seq -1 $forecast_days); do
    end=$(date +%Y%m%d -d "$yesterday + $day days")
    echo -n "Clearing old forecast $yesterday-$end "
    for var in CUR SAL SSH TEM; do
        dir=MetO-NWS-PHYS-hi-${var}
        file=metoffice_foam1_amm7_NWS_${var}_b${yesterday}_hi${end}.nc
        if [ -f $dir/$file ]; then
            rm $dir/$file
        fi
    done
    echo "done."
done

# Create a residual of the currents and sea surface height for the files we've just downloaded.
#module load mpi/mpich-x86_64
#cd ~/Models/FVCOM/fvcom-projects/stemm-ccs/python/tides/
#for day in $(seq -1 $forecast_days); do
#    day=$(date +%Y%m%d -d "$today + $day days")
#    mpirun -n $(nproc) python3 nemo_tides.py ${day:0:4} ${day:4:2} ${day:6:2} SSH sossheig
#    #mpirun -n $(nproc) python3 nemo_tides.py ${day:0:4} ${day:4:2} ${day:6:2} CUR vozocrtx
#    #mpirun -n $(nproc) python3 nemo_tides.py ${day:0:4} ${day:4:2} ${day:6:2} CUR vomecrty
#done
##python3 make_residual.py ${today:0:4} ${today:4:2} SSH sossheig
##python3 make_residual.py ${today:0:4} ${today:4:2} CUR vozocrtx
##python3 make_residual.py ${today:0:4} ${today:4:2} CUR vozocrtx
