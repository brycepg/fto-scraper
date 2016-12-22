"""Generating Statistics from fto data.

TODO
    - group by day instead of month initially since months
        do not have a uniform amount of time.i
"""

import datetime

# pylint: disable=unused-import
from typing import Tuple, Iterable, Iterator
import attr
import pandas as pd


def generate_monthly_dataframe(fto_df):
    # type: (pd.DataFrame) -> pd.DataFrame
    """Generate monthly statistics from interval dataframe.

    Returns:

        A dataframe with the following columns:

        - "Births"(int): The minimum number of births that
            occured in the month.
        - "Deaths"(int): The minimum number of deaths that
            occured in that month.
        - "Pregnancies"(int): The minimum number of pregnancies ''
        - "Months"(str): The given month and year in human readable format

        The exact number of births and deaths cannot be directly determined
        since a birth and a death can cancel out. The given data is the lower
        bound.
    """
    population_delta = create_delta(fto_df["Population"])
    mother_delta = create_delta(fto_df["Pregnant Mothers"])
    deltas = (
        (population_delta[population_delta > 0], "Births"),
        (population_delta[population_delta < 0].abs(), "Deaths"),
        (mother_delta[mother_delta > 0], "Pregnancies"),
    )
    monthly_series = (process_delta(*args) for args in deltas)
    monthly_df = pd.concat(monthly_series, axis=1).reset_index()
    return monthly_df


def create_delta(series):
    # type: (pd.Series) -> pd.Series
    """Create delta of the given series

    Column with the values (1 2 3 1)
        Would return (1 1 -2)

    Note:
        The return series will have one row less
        than the input series

    >>> delta(pd.Series([1,2,3,1])).values
    array([1, 1, -2])
    """
    dtype = series.dtype
    return (series - series.shift()).dropna().astype(dtype)


def average_stats(fto_df, monthly_df):
    # type: (pd.DataFrame, pd.DataFrame) -> Tuple[Record, ...]
    """Generate summary statistic records from fto data.

    Args:
        fto_df: fto interval data
        monthly_df: fto monthly data derived from fto_df

    Returns:
        A tuple of Record objects, denoting the name, value, and units
        of the summary metric.
    """
    min_births = monthly_df["Births"]
    min_pregnancies = monthly_df["Pregnancies"]
    avg_births_per_month = min_births.mean()
    interval_birth_queue = fto_df["Birth Queue"]
    avg_birth_queue_size = interval_birth_queue.mean()
    current_birth_queue_size = interval_birth_queue.iloc[-1]

    avg_num_babies_per_pregnancy = (min_births / min_pregnancies).mean()
    average_birth_queue_months = (avg_birth_queue_size / avg_births_per_month)
    birth_queue_now = (current_birth_queue_size / avg_births_per_month)

    return (
        Record("Average Birth Queue Time",  # type: ignore
               average_birth_queue_months,
               "months"),

        Record("Projected Birth Queue Time Entering Now",  # type: ignore
               birth_queue_now,
               "months"),

        Record("Average Number of Babies per Pregnancy",  # type: ignore
               avg_num_babies_per_pregnancy,
               "babies"),
    )


def process_delta(delta, name):
    # type: (pd.Series, str) -> pd.Series
    """Take a delta of a column
    """
    delta_per_month_gb = pd.groupby(
        delta, by=[delta.index.year, delta.index.month]
    )
    # Drop the first month
    # Shifts turn dtype into floating point, return to int
    delta_per_month = delta_per_month_gb.sum().iloc[1:]
    delta_per_month.index.name = "Month"
    delta_per_month.index = delta_per_month.index.to_series().apply(
        pretty_month)
    delta_per_month.name = name
    return delta_per_month


def pretty_month(row):
    # type: (tuple[int, int]) -> str
    """Create a human readable month from a year,month tuple."""
    year, month = row
    return datetime.datetime(
        year=year, month=month, day=1).strftime("%B %Y")


@attr.s(frozen=True)
class Record(object):
    """Return record for summary data."""
    name = attr.ib()   # type: str
    value = attr.ib()  # type: float
    unit = attr.ib()   # type: str


class RecordFormatList(object):
    """An adaptor to convert a list of records into formatted key, values"""
    def __init__(self, data):
        # type: (Iterable[Record]) -> None
        self.data = data

    def __iter__(self):
        # type: () -> Iterator[Tuple[str, str]]
        for record in self.data:
            key = record.name
            value = "%.1f %s" % (record.value, record.unit)
            yield (key, value)
