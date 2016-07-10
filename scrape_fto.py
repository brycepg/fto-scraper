#!/usr/bin/env python
from bs4 import BeautifulSoup
import requests

import time
import re

def main():
    # Grab the data
    main_page_soup = get_page_soup("http://www.faerytaleonline.com/")
    signup_page_soup = get_page_soup("http://www.faerytaleonline.com/signup.php")

    # Parse and format the data
    csv_line = ','.join([csv_format_time(),
                         get_population(main_page_soup),
                         get_birth_queue_size(signup_page_soup),
                         get_pregnant_mothers(signup_page_soup)])

    print(csv_line)

def get_page_soup(url):
    """Get html from url, parse it into beautiful soup data structure"""
    page = requests.get(url)
    c = page.content
    soup = BeautifulSoup(c, "html.parser")
    return soup

def get_population(soup):
    """Returns population size string from soup of main page"""
    population_container = soup(text=re.compile("Population:"))
    # Split by colin in first(only) match. get number after colin. Strip whitespace
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
