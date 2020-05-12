#!/bin/bash 
ncks -d time,0,23 /data/sthenno1/scratch/modop/Model/FVCOM_rosa/output/2020-05-07/aqua_v16_0001.nc temp.nc 
ncks --ppc default=4 temp.nc aqua_v16_2020-05-06.nc 
mv aqua_v16_2020-05-06.nc /data/sthenno1/scratch/modop/Model/FVCOM_rosa/output/recent_archive//aqua_v16_2020-05-06.nc
rm temp.nc 
