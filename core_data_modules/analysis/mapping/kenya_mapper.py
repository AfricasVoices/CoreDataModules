import matplotlib.pyplot as plt
from shapely import unary_union

from core_data_modules.analysis.mapping import mapping_utils


def export_kenya_constituencies_map(constituency_frequencies, file_path, region_filter=None,
                                    legend_position="lower right"):
    """
    Exports a choropleth map of Kenya's constituencies, with each constituency shaded according to the given frequency
    for each constituency.

    :param constituency_frequencies: Dictionary of Kenya constituency code -> frequency count
    :type constituency_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    :param region_filter: A function which, given a constituency name, returns whether the constituency should be drawn
                          in the exported map.
    :type region_filter: func of str -> boolean
    :param legend_position: Where on the map to draw the legend. For accepted values, see `loc` at
                            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
    :type legend_position: str
    """
    constituencies_map = mapping_utils.get_standard_geodata("kenya", "constituencies")
    if region_filter is not None:
        constituencies_map = constituencies_map[constituencies_map.ADM2_AVF.apply(region_filter)]

    lakes_map = mapping_utils.get_standard_geodata("kenya", "lakes")
    lakes_map = lakes_map[lakes_map.LAKE_AVF.isin({"lake_turkana", "lake_victoria"})]

    # Clip lakes geometry to constituencies geometry.
    constituency_geometry = unary_union(constituencies_map["geometry"])
    lakes_map["geometry"] = lakes_map["geometry"].intersection(constituency_geometry)

    fig, ax = plt.subplots()

    # Draw the base map
    mapping_utils.plot_frequency_map(
        constituencies_map, "ADM2_AVF", constituency_frequencies, ax=ax, legend_position=legend_position
    )

    if region_filter is None:
        # Draw a zoomed inset map of  Nairobi because the constituencies here are really small
        mapping_utils.plot_inset_frequency_map(
            constituencies_map, "ADM2_AVF", constituency_frequencies,
            inset_region=(36.62, -1.46, 37.12, -1.09), zoom=3, inset_position=(35.60, -2.95), ax=ax
        )

    # Draw Kenya's lakes
    if not lakes_map["geometry"].is_empty.all():
        mapping_utils.plot_water_bodies(lakes_map, ax=ax)

    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()


def export_kenya_counties_map(county_frequencies, file_path, region_filter=None, legend_position="lower right"):
    """
    Exports a choropleth map of Kenya's counties, with each county shaded and labelled according to the given frequency
    for each county.

    :param county_frequencies: Dictionary of Kenya county code -> frequency count
    :type county_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    :param region_filter: A function which, given a county name, returns whether the county should be drawn in the
                          exported map.
    :type region_filter: func of str -> boolean
    :param legend_position: Where on the map to draw the legend. For accepted values, see `loc` at
                            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
    :type legend_position: str
    """
    counties_map = mapping_utils.get_standard_geodata("kenya", "counties")
    if region_filter is not None:
        counties_map = counties_map[counties_map.ADM1_AVF.apply(region_filter)]

    lakes_map = mapping_utils.get_standard_geodata("kenya", "lakes")
    lakes_map = lakes_map[lakes_map.LAKE_AVF.isin({"lake_turkana", "lake_victoria"})]

    # Clip lakes geometry to counties geometry.
    country_geometry = unary_union(counties_map["geometry"])
    lakes_map["geometry"] = lakes_map["geometry"].intersection(country_geometry)

    fig, ax = plt.subplots()

    # Draw the base map
    mapping_utils.plot_frequency_map(counties_map, "ADM1_AVF", county_frequencies, ax=ax,
                                     label_position_columns=("ADM1_LX", "ADM1_LY"),
                                     legend_position=legend_position,
                                     callout_position_columns=("ADM1_CALLX", "ADM1_CALLY"))

    # Draw Kenya's lakes
    if not lakes_map["geometry"].is_empty.all():
        mapping_utils.plot_water_bodies(lakes_map, ax=ax)

    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()
