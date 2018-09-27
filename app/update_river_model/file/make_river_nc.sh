#!/usr/bin/env bash



date_list=
matching_files=

for i in {1..5}; do echo $(date -I -d "2014-06-15 +$i days"); done


ncrcat -v T2,RAINNC,Times wrfout_d03_${THIS_YEAR}-${THIS_MONTH}*18_00_00 -O ${THIS_YEAR}_${THIS_MONTH}_data.nc
