#!/bin/bash
output_csv=$1
if [ -z "$1" ]; then
    echo "Appends fto stats to csv file. For use in crontab"
    echo "Usage: ./append_csv <csv_name>"
    exit 1
fi

script_dir=`dirname "${BASH_SOURCE[0]}"`
csv_line=`$script_dir/scrape_fto.py`

# Exit early if there is no data from the server / scrape_fto script
if [ -z "$csv_line" ]; then
    echo "Could not get data from fto server"
    exit
fi

# Output header if the file is initially non-existent
# Do not create an empty file or this will not work
if [ ! -f $output_csv ]; then
        echo "Date,Population,Birth Queue,Pregnant Mothers" >> $output_csv
fi

# Append new data to bottom of csv
echo "$csv_line" >> $output_csv

# Run truncation script for last 6 months
$script_dir/truncate_csv.sh $output_csv ${output_csv%.csv}_6months.csv 6
