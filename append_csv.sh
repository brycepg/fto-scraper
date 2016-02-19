#!/bin/bash
output_csv=$1
if [ -z "$1" ]; then
    echo "Appends fto stats to csv file. For use in crontab"
    echo "Usage: ./append_csv <csv_name>"
    exit 1
fi

script_dir=`dirname "${BASH_SOURCE[0]}"`
csv_line=`$script_dir/scrape_fto.py`

if [ ! -f $output_csv ]; then
        echo "Date,Population,Birth Queue,Pregnant Mothers" >> $output_csv
fi

if [ -z "$csv_line" ]; then
    echo "Could not get data from fto server"
    exit
fi

echo "$csv_line" >> $output_csv

$script_dir/truncate_csv.sh $output_csv ${output_csv%.csv}_6months.csv 6
