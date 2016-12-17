#!/usr/bin/env python
"""Scrape data from the faerytaleonline website an output to stdout."""


import argparse
import time
import re


from bs4 import BeautifulSoup
import requests

class DataRepresentation(str):
    def __init__(self, string):
        valid_states = ["csv", "space", "lists"]
        if string not in valid_states:
            raise ValueError("'{}' must be in {}"
                             .format(string, valid_states))

def main():
    """Apply cli-arguments to program."""
    vargs = vars(parse_args())
    for line in run(**vargs):
        print(line)

def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--header', dest="header_enabled",
                        action='store_true', default=False)
    format_parser = parser.add_mutually_exclusive_group()
    format_parser.add_argument('--csv', help=argparse.SUPRESS,
                               action='store_true', default=True)
    format_parser.add_argument('--spaces', help=argparse.SUPRESS,
                        action='store_true', default=False)
    args = parser.parse_args()
    return args

def run(header_enabled=False,
        base_url="http://www.faerytaleonline.com",
        repr="list"):

    repr_obj = DataRepresentation(repr)
    main_page_soup = get_page_soup(base_url)
    signup_page_soup = get_page_soup("{base_url}/signup.php"
                                     .format(base_url=base_url))

    # Parse and format the data
    header = ["Date", "Birth Queue", "Population", "Pregnant Mothers"]
    data = [csv_format_time(), get_population(main_page_soup),
            get_birth_queue_size(signup_page_soup),
            get_pregnant_mothers(signup_page_soup)]
    if csv:
        header = ','.join(header)
        data = ','.join(data)

    if header:
        yield
    yield data


def get_page_soup(url):
    """Get html from url, parse it into beautiful soup data structure"""
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    return soup


def get_population(soup):
    """Returns population size string from soup of main page"""
    population_container = soup(text=re.compile("Population:"))
    # Split by colon in first(only) match. get number after colon.
    population_str = population_container[0].split(":")[1].strip()
    return population_str


def get_birth_queue_size(soup):
    """Returns birth queue size string from soup of signup page"""
    # Contains the description text but not the number
    almost_elem = soup(text=re.compile("Current size of birth queue"))[0]
    # The birth queue size is in the next element over
    birth_queue_size = almost_elem.next.text.strip()
    return birth_queue_size

def get_pregnant_mothers(soup):
    """Returns number of pregnant mothers string from soup of signup page"""
    # Same as birth queue size
    almost_elem = soup(text=re.compile("Number of pregnant"))[0]
    pregnant_mothers = almost_elem.next.text.strip()
    return pregnant_mothers

def csv_format_time():
    """Get time in correct format for google docs"""
    return time.strftime("%m/%d/%y-%H", time.gmtime())

if __name__ == "__main__":
    main()
