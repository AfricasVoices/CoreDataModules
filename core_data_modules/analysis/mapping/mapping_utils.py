try:
    import geopandas as geopandas
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas
    from mapclassify import FisherJenks
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Patch
    from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes

    import importlib.resources as resources
except ImportError as e:
    raise ImportError("A mapping dependency couldn't be imported. To use the core_data_modules.analysis.mapping "
                      "module, make sure core_data_modules' `mapping` extra is installed") from e

from core_data_modules.analysis.mapping.geojson import kenya as kenya_geojson
from core_data_modules.analysis.mapping.geojson import somalia as somalia_geojson
from core_data_modules.logging import Logger

log = Logger(__name__)


_AVF_COLOR_MAP = LinearSegmentedColormap.from_list("avf_color_map", ["#ffffff", "#993e46"])
_WATER_COLOR = "#edf5ff"


# Cache standard geojson for speed when generating lots of maps.
_geodata_cache = dict()


def get_standard_geodata(country, admin_level):
    """
    Gets the geometry for one of the standard geo-datasets provided by CoreDataModules.

    :param country: Country to retrieve the geo-dataset for.
    :type country: "kenya" | "somalia"
    :param admin_level: Map type to retrieve.
                        If `country` is "kenya", the valid values are:
                         - "counties"
                         - "constituencies"
                         - "lakes"
                        If `country` `is "somalia", the valid values are:
                         - "regions"
                         - "districts"
                         - "mogadishu sub districts"
    :type admin_level: str
    :return: GeoDataFrame for the requested dataset.
    :rtype: geopandas.GeoDataFrame
    """
    if (country, admin_level) not in _geodata_cache:
        if country == "kenya":
            module = kenya_geojson
        elif country == "somalia":
            module = somalia_geojson
        else:
            raise ValueError("Only 'kenya' and 'somalia' are supported as valid countries")

        with resources.path(module, f"{admin_level}.geojson") as f:
            _geodata_cache[(country, admin_level)] = geopandas.read_file(f)

    return _geodata_cache[(country, admin_level)].copy()


def plot_frequency_map(geo_data, admin_id_column, frequencies, label_position_columns=None,
                       callout_position_columns=None, show_legend=True, legend_position="lower right", ax=None):
    """
    Plots a map of the given geo data with a choropleth showing the frequency of responses in each administrative
    region.

    The map is plotted to the specified axes or to the active matplotlib figure.
    Use matplotlib.pyplot to access and manipulate the result.

    :param geo_data: GeoData to plot.
    :type geo_data: geopandas.GeoDataFrame
    :param admin_id_column: Column in `geo_data` of the administrative region ids.
    :type admin_id_column: str
    :param frequencies: Dictionary of admin_id -> frequency.
    :type frequencies: dict of str -> int
    :param label_position_columns: A tuple specifying which columns in the `geo_data` contain the positions to draw
                                   each frequency label at, or None.
                                   The format is (X Position Column, Y Position Column). Positions should be in
                                   the same coordinate system as the geometry, and represent the vertical and
                                   horizontal center position of the drawn label.
                                   If None, no frequency labels are drawn.
    :type label_position_columns: (str, str) | None
    :param callout_position_columns: A tuple specifying which columns in the `geo_data` contain the positions to
                                     draw callout lines to, or None.
                                     The format is (X Position Column, Y Position Column). Positions should be in
                                     the same coordinate system as the geometry, and represent the target location
                                     to draw the callout line to. The callout line is drawn from the label_position
                                     for this feature.
                                     If None, no callout lines are drawn.
    :type callout_position_columns: (str, str) | None
    :param show_legend: Whether to draw a legend for the choropleth. The legend will be drawn to the bottom-right
                        corner.
    :type show_legend: bool
    :param ax: Axes on which to draw the plot. If None, draws to a new figure.
    :type ax: matplotlib.pyplot.Artist | None
    """
    # Class the frequencies using the Fisher-Jenks method, a standard GIS algorithm for choropleth classification.
    # Using this method prevents a region with a vastly higher frequency than the others (e.g. a capital city)
    # from using up all of the colour range, as would happen with a linear scale.
    # Ignores zeros when classing, so that 0s are not included in the same class as other lower numbers, then adds
    # the 0 back in when converting from classes to bin edges.
    frequencies_to_class = [f for f in frequencies.values() if f != 0]
    number_of_classes = min(5, len(set(frequencies_to_class)))
    bin_edges = [0]
    if number_of_classes == 1:
        # FisherJenks hits a RuntimeWarning when there is only 1 class, so handle this case directly.
        bin_edges.append(max(frequencies_to_class))
    elif number_of_classes > 1:
        bin_edges.extend(FisherJenks(np.array(frequencies_to_class), k=number_of_classes).bins)

    # Get the color for each region by searching for the appropriate bin for each frequency.
    colors = []
    for i, admin_region in geo_data.iterrows():
        frequency = frequencies[admin_region[admin_id_column]]
        bin_id = [i for i, b in enumerate(bin_edges) if b >= frequency][0]  # Index of first bin edge >= frequency
        colors.append(_AVF_COLOR_MAP(0 if bin_id == 0 else float(bin_id) / number_of_classes))

    # Plot the choropleth map.
    ax = geo_data.plot(ax=ax, color=colors, linewidth=0.1, edgecolor="black")
    plt.axis("off")

    # Add the choropleth legend.
    if show_legend:
        legend_elements = [
            Patch(label="0", facecolor=_AVF_COLOR_MAP(0), linewidth=0.1, edgecolor="black")
        ]
        for bin_id in range(1, len(bin_edges)):
            range_min = bin_edges[bin_id - 1] + 1
            range_max = bin_edges[bin_id]
            legend_elements.append(Patch(
                label=int(range_min) if range_min == range_max else f"{int(range_min)} - {int(range_max)}",
                facecolor=_AVF_COLOR_MAP(float(bin_id) / number_of_classes),
                linewidth=0.1, edgecolor="black"
            ))
        ax.legend(handles=legend_elements, title="Participants", title_fontsize=6, loc=legend_position,
                  frameon=False, handlelength=1.8, handleheight=1.8, labelspacing=0, prop=dict(size=5.5))

    # Add a label to each administrative region showing its absolute frequency.
    if label_position_columns is not None:
        for i, admin_region in geo_data.iterrows():
            # Skip rows that don't have a label x/y position set.
            # If we don't skip here, we'll get a very cryptic StopIteration error much later.
            if pandas.isna(admin_region[label_position_columns[0]]) or \
                    pandas.isna(admin_region[label_position_columns[1]]):
                log.warning(f"No label positions provided for admin region '{admin_region[admin_id_column]}'")
                continue

            # Set label and callout positions from the features in the geo_data,
            # translating from the geo_data format to the matplotlib format.
            if callout_position_columns is None or pandas.isna(admin_region[callout_position_columns[0]]):
                # Draw label only.
                xy = (admin_region[label_position_columns[0]], admin_region[label_position_columns[1]])
                xytext = None
            else:
                # Draw label and callout line.
                xy = (admin_region[callout_position_columns[0]], admin_region[callout_position_columns[1]])
                xytext = (admin_region[label_position_columns[0]], admin_region[label_position_columns[1]])

            plt.annotate(text=frequencies[admin_region[admin_id_column]],
                         xy=xy, xytext=xytext,
                         arrowprops=dict(facecolor="black", arrowstyle="-", linewidth=0.1, shrinkA=0, shrinkB=0),
                         ha="center", va="center", fontsize=3.8)


def plot_inset_frequency_map(geo_data, admin_id_column, frequencies, inset_region, inset_position, zoom, ax):
    """
    Plots a map of the given geo data with a choropleth showing the frequency of responses in each administrative
    region as an inset on another axes.

    :param geo_data: GeoData to plot.
    :type geo_data: geopandas.GeoDataFrame
    :param admin_id_column: Column in `geo_data` of the administrative region ids.
    :type admin_id_column: str
    :param frequencies: Dictionary of admin_id -> frequency.
    :type frequencies: dict of str -> int
    :param inset_region: Map co-ordinates to plot in the inset map, in the form (x1, y1, x2, y2).
    :type inset_region: (float, float, float, float)
    :param inset_position: Map co-ordinates to center the inset on, in the form (x, y).
    :type inset_position: (float, float)
    :param zoom: Zoom factor.
    :type zoom: float
    :param ax: Axes on which to draw the plot. If None, draws to a new figure.
    :type ax: matplotlib.pyplot.Axes
    """
    inset_ax = zoomed_inset_axes(ax, zoom=zoom, loc="center", bbox_to_anchor=inset_position,
                                 bbox_transform=ax.transData)
    plt.setp(inset_ax.spines.values(), linewidth=0.2, color="black")
    inset_ax.set_xlim(inset_region[0], inset_region[2])
    inset_ax.set_ylim(inset_region[1], inset_region[3])
    inset_ax.set_xticklabels('')
    inset_ax.set_yticklabels('')
    rectangle, connectors = ax.indicate_inset_zoom(inset_ax, edgecolor="black", alpha=1, linewidth=0.2)
    for c in connectors:
        c.set_visible(False)
    inset_ax.xaxis.set_visible(False)
    inset_ax.yaxis.set_visible(False)

    plot_frequency_map(geo_data, admin_id_column, frequencies, ax=inset_ax, show_legend=False)
    inset_ax.axis("on")


def plot_water_bodies(geo_data, ax=None):
    """
    Plots a map of the given `geo_data`, shaded with color `_WATER_COLOR`.

    The map is plotted to the specified axes or to the active matplotlib figure.
    Use matplotlib.pyplot to access and manipulate the result.

    :param geo_data: GeoData to plot.
    :type geo_data: geopandas.GeoDataFrame
    :param ax: Axes on which to draw the plot. If None, draws to a new figure.
    :type ax: matplotlib.pyplot.Artist | None
    """
    geo_data.plot(ax=ax, linewidth=0.1, edgecolor="black", facecolor=_WATER_COLOR)
