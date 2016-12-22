"""A package for scraping analyzing, and graphing faery tale online data.

- scrape_fto: extracts the data from the fto website into csv form

- fto_graph: takes the collected data and generates a static graph

- fto_web: generates an interactive graph of the collected data

- stats: generates statistic from the collected data (not finished)

"""
from .scrape_fto import run as scrape
from .fto_graph import run as graph
from .fto_graph import load_dataframe
