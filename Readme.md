Grabs data from faerytailonline webpage for use in a csv in the following format:

    MM/DD/YY-HH, Population, Birth Queue Size, Pregnant Mothers

where the time is UTC. HH is in 24 hour format

# Requirements

    Python2 or Python3
    Bash
    beautifulsoup4 (python library)
    requests (python library)

# Installation

    sudo apt-get install python3 python3-pip
    sudo pip install beautifulsoup4 requests


# Usage

## scrape_fto.py

    ./scrape-fto.py 

Queries fto and echos the formatted string 

## append_csv.sh

Calls the above python script and appends the output
to a csv and creats headers if emtpy. 
This script should be called by crontab at regular intervals and 
the output csv should be accessable via http

e.g.

        ./append_csv.sh output.csv


A crontab entry might look like

        0 0,12 * * * /dir/append_csv.sh /var/www/fto-stats.csv

which runs the script twice per day at 12AM / 12PM
where `dir` is the directory for `append_csv.sh` AND `scrape_fto.py` 

### Output

        Date,Population,Birth Queue,Pregnant Mothers
        02/15/16-08,311,152,3

Once the csv is accessable via http, it can be linked into a google doc, 
and graphs can be applied to the data
