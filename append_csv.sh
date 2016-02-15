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

echo "$csv_line" >> $output_csv
