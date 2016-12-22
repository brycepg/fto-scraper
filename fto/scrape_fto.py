#!/usr/bin/env python
"""Scrape data from the faerytaleonline website an output to stdout."""


import argparse
import time
import re


# pylint: disable=unused-import
from typing import Any, Iterable, Union # NOQA
from bs4 import BeautifulSoup
import requests


def main():
    """Apply cli-arguments to program."""
    # type: () -> None
    vargs = parse_args()
    for line in run(**vargs):
        print(line)


def parse_args():
    # type: () -> dict[str, Any]
    """Parse program arguments. Return dict of arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--header', dest="header_enabled",
                        action='store_true', default=False)
    vargs = vars(parser.parse_args())
    vargs['output_csv'] = True
    return vargs


def run(header_enabled=False,
        base_url="http://www.faerytaleonline.com",
        output_csv=False):
    # type: (bool, str, bool) -> Iterable[Union[List[str], str]]
    """Main entry point for scraping data.

    Args:
        header_enabled: if True, output headers for given data
        base_url: Url to website to parse
        output_csv: If true csv instead of list

    Yields:
        The scraped data and optionally the header.
        """
    main_page_soup = get_page_soup(base_url)
    signup_page_soup = get_page_soup("{base_url}/signup.php"
                                     .format(base_url=base_url))

    # Parse and format the data
    header = [
        "Date", "Birth Queue", "Population",
        "Pregnant Mothers"]  # type: Union[List[str], str]
    data = [
        csv_format_time(), get_population(main_page_soup),
        get_birth_queue_size(signup_page_soup),
        get_pregnant_mothers(signup_page_soup)]  # type: Union[List[str], str]

    if output_csv:
        header = ','.join(header)  # pylint: disable=redefined-variable-type
        data = ','.join(data)  # pylint: disable=redefined-variable-type

    if header_enabled:
        yield header
    yield data


def get_page_soup(url):
    # type: (str) -> BeautifulSoup
    """Get html from url, parse it into beautiful soup data structure"""
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    return soup


def get_population(soup):
    # type: (BeautifulSoup) -> str
    """Returns population size string from soup of main page"""
    population_container = soup(text=re.compile("Population:"))
    # Split by colon in first(only) match. get number after colon.
    population_str = population_container[0].split(":")[1].strip()
    return population_str


def get_birth_queue_size(soup):
    # type: (BeautifulSoup) -> str
    """Returns birth queue size string from soup of signup page"""
    # Contains the description text but not the number
    almost_elem = soup(text=re.compile("Current size of birth queue"))[0]
    # The birth queue size is in the next element over
    birth_queue_size = almost_elem.next.text.strip()
    return birth_queue_size


def get_pregnant_mothers(soup):
    # type: (BeautifulSoup) -> str
    """Returns number of pregnant mothers string from soup of signup page"""
    # Same as birth queue size
    almost_elem = soup(text=re.compile("Number of pregnant"))[0]
    pregnant_mothers = almost_elem.next.text.strip()
    return pregnant_mothers


def csv_format_time():
    # type: () -> str
    """Get time in correct format for google docs"""
    return time.strftime("%m/%d/%y-%H", time.gmtime())

if __name__ == "__main__":
    main()
