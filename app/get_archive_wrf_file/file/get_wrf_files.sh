#!/bin/bash

START_DAY=$1
END_DAY=$2
WRF_ARCHIVE_DATEFMT=$3
WRF_ARCHIVE_DIR=$4
ROSE_DATAC=$5

echo 1
echo ${START_DAY} 

echo 2
echo ${END_DAY} 

echo 3
echo ${WRF_ARCHIVE_DATEFMT} 

echo 4
echo ${WRF_ARCHIVE_DIR}

echo 5
echo ${ROSE_DATAC}


d_comp=0
n=0
until [ "$d_comp" = "$END_DAY" ]
do
    ((n++))
    d=$(date -d "$START_DAY + $n days" +${WRF_ARCHIVE_DATEFMT})
    d_comp=$(date -d "$START_DAY + $n days" +%Y-%m-%d)
    cp /pml${WRF_ARCHIVE_DIR}/*${d}*/wrfout_d03_* raw_wrf_file_${n}.nc
done
