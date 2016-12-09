#!/usr/bin/env python
"""Command-line program to read a fto statistics csv and output a png graph"""

import argparse
import errno
import logging
import sys
from operator import itemgetter

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
# Removes dependency on graphical system
matplotlib.use('Agg')

plt.style.use('bmh')
matplotlib.rcParams.update({'font.size': 22})

# Convention
# pylint: disable=invalid-name
log = logging.getLogger(__name__)


class Error(Exception):
    """All errors in this module inherit from this class."""
    pass


class CSVNotReadError(Error):
    """Error for failing to retrieve data from `input_csv`"""
    def __init__(self, msg, errno_):
        super(CSVNotReadError, self).__init__(msg)
        self.msg = msg
        self.errno = errno_


class CSVNotFoundError(Error):
    """Error when the `input_csv` argument is not found"""
    pass


class InvalidCSVError(Error):
    """Error when the data inside the csv doesn't make sense."""
    pass


def main():
    """Feed command-line argument dict into service."""
    logging.basicConfig(level=logging.INFO)

    vargs = vars(parse_args())
    if vargs['verbose']:
        logging.getLogger().setLevel(level=logging.DEBUG)
        log.setLevel(level=logging.DEBUG)
    try:
        run(vargs)
    except KeyboardInterrupt as e:
        log.debug(e, stack_info=True)
        log.info("Keyboard Cancelled operation")
    except Error as e:
        log.debug(e, stack_info=True)
        log.error("Could not generate figure: %s", str(e))
        sys.exit(1)

    print("%s => %s" % itemgetter('input_csv', 'output_filename')(vargs))


def parse_args():
    """Parses command-line arguments and stuffs them into a namespace.

    Returns a argparse.Namespace of arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv', help='path to fto statistic CSV')
    parser.add_argument(
        'output_filename', nargs='?',
        help='output PNG filename', default='output.png'
    )
    parser.add_argument(
        '--verbose', help='Turn debug output on.', action='store_true')
    args = parser.parse_args()
    return args


def get_mapped_vals(data_dict, keys):
    """Get the data from each key in `keys` from `data_dict`.

    Args:
        data_dict(dict): A container which must contains all of `keys`
        keys(list): A list of keys to pull from `data_dict`

    Returns:
        A list of in-order values from the container `keys`
    """
    values = []
    for key in keys:
        values.append(data_dict[key])
    return values


def run(vargs):
    """parse csv, modify dataframe, generate figure, save figure.

    Args:
        vargs(dict): A dictionary of arguments to this function.

    Side effects:
        saves figure at `args['output_filename']`
    Returns:
        A copy of the figure
    """

    df = load_dataframe(vargs['input_csv'])
    figure = generate_figure(df)
    figure.savefig(vargs['output_filename'])
    return figure


def load_dataframe(csv_path):
    """Load pd.DataFrame from csv at `csv_path` on the filesystem.

    Args:
        csv_path(str): Path to existing csv on filesystem

    Returns:
        A `pd.DataFrame` with the column names 'Birth Queue',
        'Population', and 'Pregnant Mothers'. Indexed by date of
        occurance accurate up to an hour.

    Raises:
        CSVNotReadError if data from `csv_path` cannot be read from.
        InvalidCSVError if the data in `csv_path` is not valid for this
        program.
    """
    columns = ['Date', 'Birth Queue', 'Population', 'Pregnant Mothers']
    line = ""
    try:
        with open(csv_path) as csv_fh:
            line = csv_fh.readline()
            names = None if substrs_in_line(columns, line) else columns
            csv_fh.seek(0)
            # Supply column names if not present
            # If present, do not supply column names
            # since supplying column names while having
            # column names in the csv leads to a row for data
            # with column names.
            df = pd.read_csv(csv_fh, names=names)
    except (OSError, IOError) as e:
        if e.errno == errno.ENOENT:
            raise CSVNotFoundError(
                "Could not find csv at %s" % csv_path, e.errno)
        else:
            raise CSVNotReadError(
                "Could not retrieve data from csv %s" % csv_path, e.errno)

    # Data verification
    for col in columns:
        # Pylint is confused by df.columns
        # pylint: disable=no-member
        if col not in df.columns:
            raise InvalidCSVError("Column '%s' not present in input csv %s "
                                  "but should be" % (col, csv_path))
    # Reindex dataframe based on date column
    df.index = pd.to_datetime(df['Date'], format='%m/%d/%y-%H')
    del df["Date"]
    return df


def substrs_in_line(items, line):
    """Returns True if `line` contains any item from `items` else False.

    Args:
        items(list[str]): A container of substrings to test.
        line(str): A string which may contain any string in `items`

    Returns:
        A bool indicating whether `line` contains any of `items`"""
    for item in items:
        if item not in line:
            return False
    return True


def generate_figure(df):
    """Generates a matplotlib.figure.Figure from `df`.

    Takes the fto-data dataframe, plots Population, Birth Queue, and Pregnant
    Mothers onto a matplotlib figure.

    Args:
        df(pd.DataFrame): The fto dataframe index by datetime.

    TODO:
        Remove 0 label for pregnant mothers

    Returns:
        The generated matplotlib figure.
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
    ax_secondary.plot(df['Birth Queue'],
                      color=birth_queue_color, clip_on=False, linewidth=5)

    # Pregnant mothers
    preg_label = "Pregnant Mothers"
    # Use lower 1/3 of graph
    ax_lower = plt.subplot2grid((3, 1), (2, 0), rowspan=1)
    ax_lower.set_ylabel(preg_label)
    ax_lower.plot(df['Pregnant Mothers'],
                  color='g', clip_on=False, linewidth=5)

    # Start pregnant mothers y-axis at 0 even though there might not be
    # 0 pregnant mothers
    ax_lower.set_ylim(0, ax_lower.get_ylim()[1])

    # Beautiful magic to format the date xticks
    fig.autofmt_xdate()

    # Y tick marks
    # For some reason matplotlib decided pregnant mothers needs floating point
    # y tick marks - make them ints again
    # XXX test fixing this section
    yint = []
    locs, labels = plt.yticks()
    for each in locs:
        yint.append(int(each))
        plt.yticks(yint)

    return fig


if __name__ == "__main__":
    main()
