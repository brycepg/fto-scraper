#!/bin/bash

if (( $# < 2 || $# > 3 )); then
    echo "Writes the last <limit> months of <full_csv> to <short_csv>."
    echo "Usage: $(basename $0) <full_csv> <short_csv> [limit=6]"
    exit 1
fi

full_csv=$1
short_csv=$2
limit=${3:-6}

# Write the (single) header line.
head -n 1 $full_csv > $short_csv

# Take lines from the end until the threshold is passed.
threshold=$(( 12 * 10#$(date -u +%y) + 10#$(date -u +%m) - $limit ))
tac $full_csv | while read -r line; do
    # MM/DD/YY-HH
    if ! [[ "$line" =~ [0-9]{2}/[0-9]{2}/[0-9]{2}-[0-9]{2} ]]; then break; fi
    if (( 12 * 10#${line:6:2} + 10#${line:0:2} <= threshold )); then break; fi
    echo "$line"
done | tac >> $short_csv
