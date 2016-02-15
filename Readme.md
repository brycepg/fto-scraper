Grabs data from faerytailonline webpage for use in a csv in the following format:

    M/DD/YY-HH, Population, Birth Queue Size, Pregnant Mothers

where the time is UTC

# Requirements

    Python2 or Python3
    Bash
    beautifulsoup4 (python library)
    requests (python library)

# Installation

    sudo apt-get install python3 python3-pip
    sudo pip install beautifulsoup4 requests


# Usage

## scrape-fto.py

    ./scrape-fto.py 

Queries fto and echos the formatted string 

## append-csv.sh

Call the above python script and appends the output
to a csv and creats headers if emtpy. 
This script should be called by crontab and 
the output csv should be accessable via http

e.g.

        ./append-csv.sh output.csv

### Output

        Date,Population,Birth Queue,Pregnant Mothers
        02/15/16-08,311,152,3

Once the csv is accessable via http, it can be linked into a google doc, 
and graphs can be applied to the data
