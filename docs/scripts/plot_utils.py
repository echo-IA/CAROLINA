from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import matplotlib.pyplot as plt


def two_color_cmap(hex1, hex2, n=256, name='two_color'):
    """
    Create a linear colormap that blends from hex1 → hex2.

    Parameters
    ----------
    hex1, hex2 : str
        The start and end colors, e.g. "#FF0000", "#0000FF".
    n : int
        Number of discrete steps in the colormap (default 256).
    name : str
        Name for the colormap.

    Returns
    -------
    cmap : LinearSegmentedColormap
    """
    return LinearSegmentedColormap.from_list(name, [hex1, hex2], N=n)


def plot_counts(series, xlabel, ylabel, outfile=None, color="#012169", figsize=(16, 5)):
    """
    Plot a bar chart of value counts from a pandas Series with Duke-blue styling.

    Parameters
    ----------
    series : pd.Series
        The data column (categorical) to count and plot.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    outfile : str or None
        Path to save the figure. If None, the figure is not saved.
    color : str
        Hex color code for all plot elements (default: Duke navy blue).
    figsize : tuple
        Figure size (default: (16, 5)).

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """

    # Count values and sort descending
    counts = series.value_counts().sort_values(ascending=False)

    # Plot
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(counts.index, counts.values, color=color)
    ax.bar_label(bars, fmt="%d", padding=5, fontsize=18, color=color)

    # Labels
    ax.set_xlabel(xlabel, fontsize=20, color=color)
    ax.set_ylabel(ylabel, fontsize=20, color=color)

    # Tick labels
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=16, color=color)
    plt.setp(ax.get_yticklabels(), fontsize=16, color=color)

    # Ticks and margins
    ax.tick_params(axis="both", colors=color, left=False, bottom=False)
    ax.margins(y=0.15)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(color)

    # Save if requested
    if outfile:
        plt.savefig(outfile, bbox_inches="tight", dpi=300, pad_inches=0.2)

    plt.show()
    return fig, ax

