#!/bin/bash --login

# Script to merge the individual runs into month long chunks ready for
# conversion with wrf_to_fvcom.

module purge
module load nco

set -eu

# Make sure any symbolic links are resolved to absolute path.
PBS_O_WORKDIR=$(pwd)
export PBS_O_WORKDIR=$(readlink -f $PBS_O_WORKDIR)

# Change to the directory from which the job was submitted.
cd $PBS_O_WORKDIR

year=${year:-2017}
srcdir=$(readlink -f $PBS_O_WORKDIR/output/)
binary=$PBS_O_WORKDIR/bin/wrf_to_fvcom_ceto
start_hour=18 # hour at which the outputs are generated
wrfnest=${wrfnest:-d03}

for rawmonth in {1..12}; do

    # Sort out our time bracket.
    yearbefore=$year
    yearafter=$year
    before=$(printf %02d $((rawmonth - 1)))
    month=$(printf %02d $rawmonth)
    after=$(printf %02d $((rawmonth + 1)))

    # If we're in January or December, reset the before and after month and
    # year to the appropriate values.
    if [ $rawmonth -eq 1 ]; then
        yearbefore=$((year - 1))
        before=12
    elif [ $rawmonth -eq 12 ]; then
        yearafter=$((year + 1))
        after=01
    fi

    # We need all the files from the current month plus a couple of days either
    # side for the FVCOM runs. We need to use an extra pattern of
    # $year/wrfout_${wrfnest}_$yearbefore-$before* for the start of a given year as
    # that may have actually been run as the last day of the previous year. In
    # that instance, the output file will be in the $year directory but will
    # actually be named $yearbefore. Limit that search to the last few days to
    # not include the whole month in a non-year-boundary month (i.e. not
    # January).
    files=($(\ls -1 $srcdir/$yearbefore/wrfout_${wrfnest}_$yearbefore-$before-{26,27,28,29,30,31}_${start_hour}?00?00 \
                    $srcdir/$year/wrfout_${wrfnest}_$yearbefore-$before-{26,27,28,29,30,31}_${start_hour}?00?00 \
                    $srcdir/$year/wrfout_${wrfnest}_$year-$month-??_${start_hour}?00?00 \
                    $srcdir/$yearafter/wrfout_${wrfnest}_$year-$month-??_${start_hour}?00?00 \
                    $srcdir/$yearafter/wrfout_${wrfnest}_$yearafter-$after-{01,02,03}_${start_hour}?00?00 2> /dev/null | sort -u))

    # Now convert to FVCOM forcing files. These files have all had their first
    # time step removed as that's just the initial condition. So, you'd need to
    # add a -dTime,1,, to the ncrcat command to drop the first time step if
    # that's not been done. Once they're all converted, ncrcat them all
    # together into a single file for this month.
    parallel \(ln -s {} current_{/.}.nc \|\| true\) \&\& $binary -i current_{/.}.nc -o /var/tmp/out_{/.}.nc -latitude 50.0 -hindcast \> \/dev\/null ::: "${files[@]}"
    parallel rm current_{/.}.nc ::: "${files[@]}"
    parallel ncrcat -O -h /var/tmp/out_{/.}.nc /var/tmp/trim_{/.}.nc ::: "${files[@]}"
    parallel rm /var/tmp/out_{/.}.nc ::: "${files[@]}"
    rm $srcdir/$year/wrfout_${wrfnest}_${year}-${month}.nc || true
    ncrcat -O -h $(\ls -1 /var/tmp/trim_wrfout_${wrfnest}_{${yearbefore},${year},${yearafter}}-{${before},${month},${after}}-??_*.nc | sort -u) $srcdir/$year/wrfout_${wrfnest}_${year}-${month}.nc
    parallel rm /var/tmp/trim_{/.}.nc ::: "${files[@]}"

done

