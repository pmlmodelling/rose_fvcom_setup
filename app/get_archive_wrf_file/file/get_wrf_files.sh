#!/bin/bash

START_DAY=$1
END_DAY=$2
WRF_ARCHIVE_DATEFMT=$3
WRF_ARCHIVE_DIR=$4

d_comp=0
n=0
until [ "$d_comp" = "$END_DAY" ]
do
    d=$(date -d "$START_DAY + $n days" +${WRF_ARCHIVE_DATEFMT})
    d_comp=$(date -d "$START_DAY + $n days" +%Y-%m-%d)
    cp /pml${WRF_ARCHIVE_DIR}/wrfout_d03_${d} raw_wrf_file_${n}.nc
    ((n++))
done
