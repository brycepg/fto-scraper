#!/usr/bin/env python

"""Command-line program to read a fto statistics csv and output a png graph"""
import argparse

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib

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

def run(args):
    """parse csv, modify dataframe, generate figure, save figure"""
    df = pd.read_csv(args.input_csv)
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
    fig = plt.figure(figsize=(20,15))

    # Population
    pop_label = "Population"
    pop_color = 'r'
    # Use 2/3 of grid
    ax = plt.subplot2grid((3,1), (0,0), rowspan=2, label=pop_label)
    ax.set_ylabel(pop_label)
    df['Population'].plot(ax=ax, style=pop_color, clip_on=False, linewidth=5)
    # Create line of same color for legend key
    # (not automatically generated for subplots)
    reds_line = mlines.Line2D([], [], color=pop_color, label=pop_label)

    # Birth Queue
    # Generate secordary axis for top subplot
    ax_secondary  = ax.twinx()
    birth_queue_label = 'Birth Queue'
    birth_queue_color = 'b'
    ax_secondary.set_ylabel(birth_queue_label)
    blue_line = mlines.Line2D([], [], color=birth_queue_color,
                              label=birth_queue_label)
    df['Birth Queue'].plot(ax=ax_secondary, style=birth_queue_color,
                           clip_on=False, linewidth=5)


    # Pregnant mothers
    preg_label = "Pregnant Mothers"
    # Use lower 1/3 of graph
    ax_lower = plt.subplot2grid((3,1), (2,0), rowspan=1)
    ax_lower.set_ylabel(preg_label)
    df['Pregnant Mothers'].plot(ax=ax_lower, style='g', clip_on=False, linewidth=5)
    # Start pregnant mothers y-axis at 0 even though there might not be 
    # 0 pregnant mothers
    ax_lower.set_ylim(0, ax_lower.get_ylim()[1])

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
    ax.legend(loc='upper center',handles=[blue_line, reds_line])

    return fig

if __name__ == "__main__":
    main()
