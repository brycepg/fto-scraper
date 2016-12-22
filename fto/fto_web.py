"""FTO data for the web using bokeh.

Generates a bokeh layout which can be used to generate a visual representation
on the HTML canvas.

"""

import argparse


# pylint: disable=unused-import
from typing import IO, Union, AnyStr  # NOQA
import bokeh
import bokeh.mpl
import bokeh.io
import bokeh.models.plots
import bokeh.plotting
import bokeh.layouts
import bokeh.charts
from bokeh.models import CustomJS
from bokeh.models import Range1d, LinearAxis
from bokeh.models import HoverTool
# pylint: disable=no-name-in-module
from bokeh.palettes import Set1_3
from bokeh.plotting import figure
import pandas as pd
import attr

from . import load_dataframe


def main():
    """Cli interface to show resultant graph in browser."""
    # type () -> None
    vargs = parse_args()
    layout = run(**vargs)
    bokeh.plotting.show(layout)


def parse_args():
    """Generate args for cli-interface."""
    # type: () -> dict[str, Any]
    parser = argparse.ArgumentParser(
        "Generate interactive web graph for fto data.")
    parser.add_argument(metavar="csv_path", dest="csv_path_or_df",
                        help="url or file system path to csv source data.")
    return vars(parser.parse_args())


def run(csv_path_or_df):
    # type: (Union[str, pd.DataFrame, IO[AnyStr]]) -> bokeh.layouts.LayoutDOM
    """Reads fto data from resource and returns a bokeh object.

    Args:
        csv_path_or_df: A path, url, DataFrame, or file-like object
            that contains fto data.

    Returns:
        A bokeh objet which can be displayed in a jupyter notebook or
            other web interface.
    """
    if isinstance(csv_path_or_df, pd.DataFrame):
        fto_df = csv_path_or_df
    else:
        fto_df = load_dataframe(csv_path_or_df)

    if "Date Formatted" not in fto_df.columns:
        fto_df["Date Formatted"] = format_bokeh_date(fto_df)
    layout = generate_bokeh_layout(fto_df)

    # It is in fact an iterable
    for child in layout.children:  # pylint: disable=not-an-iterable
        child.sizing_mode = 'scale_width'
    layout.sizing_mode = 'scale_width'
    return layout


def generate_bokeh_layout(fto_df):
    # type: (pd.DataFrame) -> bokeh.layouts.LayoutDOM
    """Generate bokeh layout from data in given DataFrame."""
    width = 1600
    pop_color, birth_color, mother_color = Set1_3
    source = bokeh.models.ColumnDataSource(fto_df)
    mother_fig = generate_mother_figure(fto_df, source, mother_color, width)

    fig_options = TopFigOptions(pop_color, birth_color, width)
    top_fig = generate_top_figure(fto_df, mother_fig, source, fig_options)
    header = bokeh.models.Div(text="<h1>FTO Hourly Statistics</h1>")
    column = bokeh.layouts.column([header, top_fig, mother_fig])

    return column


def generate_mother_figure(fto_df,        # type: pd.DataFrame
                           source,        # type: ColumnDataSource
                           mother_color,  # type: str
                           width          # type: int
                           ):  # pylint: disable=bad-continuation
                        # type: (...) -> bokeh.models.figure.Figure
    """Generate the bottom part of the bokeh layout."""
    mother_y_range = Range1d(
        0, fto_df["Pregnant Mothers"].max(), bounds="auto")
    mother_x_range = Range1d(fto_df.index[0], fto_df.index[-1], bounds="auto")
    mother_fig = figure(x_axis_label="Pregnant Mothers",
                        width=width, height=150,
                        y_range=mother_y_range, x_range=mother_x_range,
                        tools=[])
    mother_fig.xaxis.axis_label_text_font_size = '14pt'
    mother_fig.yaxis.minor_tick_line_color = None
    mother_fig.line(
        'Date', 'Pregnant Mothers', source=source,
        line_width=2, color=mother_color)
    mother_fig.toolbar.logo = None
    return mother_fig


def generate_top_figure(fto_df,       # type: pd.DataFrame
                        mother_fig,   # type: bokeh.models.figure.Figure
                        source,       # type: ColumnDataSource
                        options,      # type: TopFigOptions
                        ):  # pylint: disable=bad-continuation
                        # type (...) -> bokeh.models.figure.Figure
    """Generate the top portion figure for population and birth queue.

    Args:
        fto_df: Used to find desired reange via min/max values
        mother_fig: Used to link range with this figure's data
        source: Used to link together vlaues
        pop_color: Population color as a rgb value / name
        birth_color: Birth Queue color as a rgb value / name
        width: Width of figures.

    Returns:
        The generated figure
    """
    tools = "pan,xbox_zoom,reset"
    pop_name = "population"
    birth_queue_name = "Birth Queue"
    x_axis_name = "Date"
    birth_queue = fto_df[birth_queue_name]
    population = fto_df.Population
    fig_props = {
        'width': options.width,
        'tools': tools,
        'active_drag': 'xbox_zoom',
    }
    line_props = {
        'line_width': 3,
        'line_cap': 'round',
        'source': source,
    }
    top_fig_range = Range1d(
        birth_queue.min(), birth_queue.max(), bounds="auto")
    top_fig = figure(
        x_range=mother_fig.x_range, y_axis_label=birth_queue_name,
        y_range=top_fig_range, **fig_props)
    top_fig.line(
        x_axis_name, birth_queue_name, color=options.birth_color, **line_props)
    top_fig.yaxis.axis_label_text_color = options.birth_color
    pop_range = Range1d(
        start=population.min(), end=population.max(), bounds="auto")
    top_fig.extra_y_ranges = {pop_name: pop_range}
    pop_renderer = top_fig.line(
        x_axis_name, pop_name.capitalize(), y_range_name=pop_name,
        color=options.pop_color, **line_props)
    population_axis = LinearAxis(y_range_name=pop_name,
                                 axis_label=pop_name.capitalize(),
                                 axis_label_text_color=options.pop_color)
    top_fig.add_layout(population_axis, 'left',)
    top_fig.yaxis.axis_label_text_font_size = '16pt'
    top_fig.yaxis.axis_label_text_font_style = 'bold'
    top_fig.xaxis.visible = False
    top_fig.toolbar.logo = None
    vertical_positioner = bokeh.models.CrosshairTool(dimensions="height")
    top_fig.add_tools(vertical_positioner)
    hover_tool = generate_hover_tool([pop_renderer])
    top_fig.add_tools(hover_tool)
    return top_fig


def generate_hover_tool(renderers):
    # type: (List[bokeh.model.renderers.Renderer]) -> HoverTool
    """Generate a hover tool which is tied to the all the given renderers.

    Added some custom javascript to:

    - change the cursor back from crosshair to invisible
    - Stop the tooltip from moving on the screen

    Args:
        renderers: The renderers you want the hover tool to effect

    Returns:
        A hover tool that is tied to the given renderers

    Note:

    """
    callback = CustomJS(code="""
        var arr = document.getElementsByClassName("bk-canvas-wrapper");
        for(var i = 0, len = arr.length; i < len; i++) {
            arr[i].style.cursor = "none";
        }
        var elem = document.getElementById("static-tooltip");
        if (elem == null) {
            return;
        }
        var tooltip = elem.parentNode.parentNode.parentNode;
        tooltip.style.top = ""; // unset what bokeh.js sets
        tooltip.style.left = "";
        tooltip.style.top = "4px";
        tooltip.style.left = "122px";

        """)

    # This div is needed for the above javascript to work.
    tooltop_dom = """
    <div id="static-tooltip">
        <span>Population: @Population</span><br />
        <span>Birth Queue: @{Birth Queue}</span><br />
        <span>Pregnant Mothers: @{Pregnant Mothers}</span><br />
        <span>Date: @{Date Formatted}</span><br />
    </div>"""
    # vline allows the tooltip to be displayed verically even
    #   when not touching a line.
    hover = HoverTool(renderers=renderers,
                      mode="vline",
                      callback=callback,
                      line_policy="nearest",
                      show_arrow=False,
                      tooltips=tooltop_dom)
    return hover


def format_bokeh_date(fto_df):
    # type: (pd.DataFrame) -> pd.Series
    """Find Date on DateaFrame and return a human readable time format.

    Args:
        fto_df: A DataFrame that contains a Date column of human readable
                strings or a DataFrame indexed by DateTime.

    Returns:
        A Series of human-readable date strings.
    """
    date_format = '%m/%d/%y-%H'
    if "Date" in fto_df.columns:
        series = fto_df.Date
    else:
        series = fto_df.index.strftime(date_format)
    return series


# This class is a record-type class
# pylint: disable=too-few-public-methods
@attr.s
class TopFigOptions(object):
    """Options for top_figure"""
    pop_color = attr.ib()
    birth_color = attr.ib()
    width = attr.ib()


if __name__ == "__main__":
    main()
