#!/usr/bin/env python

"""Command-line program to read a fto statistics csv and output a png graph"""
import argparse

import pandas as pd
import matplotlib
# Removes dependency on graphical system
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

plt.style.use('bmh')
matplotlib.rcParams.update({'font.size': 22})


def main():
    """
    Get arguments from the command-line and pass them into the main function
    """
    args = parse_args()
    run(args)


def parse_args():
    """
    Parses command-line arguments and stuffs them into a namespace
    Returns the argument-namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv', help='path to fto statistic CSV')
    parser.add_argument('output_filename', nargs='?', help='output PNG filename', default='output.png')
    args = parser.parse_args()
    return args


def substrs_in_line(items, line):
        for item in items:
            if item not in line:
                return False
        return True

def run(args):
    """parse csv, modify dataframe, generate figure, save figure"""
    columns = ['Date', 'Birth Queue', 'Population', 'Pregnant Mothers']
    line = ""
    with open(args.input_csv) as csv:
        line = csv.readline()
    # Supply column names if not present
    # If present, do not supply column names
    # since that would lead to them being duplicated into
    # a row
    if substrs_in_line(columns, line):
        df = pd.read_csv(args.input_csv)
    else:
        df = pd.read_csv(args.input_csv, names=columns)


    # Reindex dataframe based on date column
    df.index = pd.to_datetime(df['Date'], format='%m/%d/%y-%H')

    figure = generate_figure(df)
    figure.savefig(args.output_filename)


def generate_figure(df):
    """
    Takes the fto-data dataframe, plots Population, Birth Queue, and Pregnant
    Mothers onto a matplotlib figure.

    Returns the genreated matplotlib figure.
    """
    fig = plt.figure(figsize=(20, 15))

    # Population
    pop_label = "Population"
    pop_color = 'r'
    # Use 2/3 of grid
    ax = plt.subplot2grid((3, 1), (0, 0), rowspan=2, label=pop_label)
    ax.set_ylabel(pop_label, color=pop_color)
    ax.plot(df['Population'], color=pop_color, clip_on=False, linewidth=5)

    # Birth Queue
    # Generate secordary axis for top subplot
    ax_secondary = ax.twinx()
    birth_queue_label = 'Birth Queue'
    birth_queue_color = 'b'
    ax_secondary.set_ylabel(birth_queue_label, color=birth_queue_color)
    ax_secondary.plot(df['Birth Queue'], color=birth_queue_color, clip_on=False, linewidth=5)

    # Pregnant mothers
    preg_label = "Pregnant Mothers"
    # Use lower 1/3 of graph
    ax_lower = plt.subplot2grid((3, 1), (2, 0), rowspan=1)
    ax_lower.set_ylabel(preg_label)
    ax_lower.plot(df['Pregnant Mothers'], color='g', clip_on=False, linewidth=5)
    # Start pregnant mothers y-axis at 0 even though there might not be
    # 0 pregnant mothers
    ax_lower.set_ylim(0, ax_lower.get_ylim()[1])

    # Beautiful magic to format the date xticks
    fig.autofmt_xdate()

    #plt.setp(ax.xaxis.get_majorticklabels(), rotation=9)

    # Y tick marks
    # For some reason matplotlib decided pregnant mothers needs floating point
    # y tick marks - make them ints again
    yint = []
    locs, labels = plt.yticks()
    for each in locs:
            yint.append(int(each))
            plt.yticks(yint)

    # Legend
    # Use top axis to generate the top subplot graph using the proper artists

    return fig

if __name__ == "__main__":
    main()
