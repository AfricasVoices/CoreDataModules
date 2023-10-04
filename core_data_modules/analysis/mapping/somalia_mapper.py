import matplotlib.pyplot as plt

from core_data_modules.analysis.mapping import mapping_utils


def export_somalia_region_frequencies_map(region_frequencies, file_path, region_filter=None,
                                          legend_position="lower right"):
    """
    Exports a choropleth map of Somalia's regions, with each region shaded and labelled according to the given
    frequency for each region.

    :param region_frequencies: Dictionary of Somalia region code -> frequency count
    :type region_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    """
    regions_map = mapping_utils.get_standard_geodata("somalia", "regions")
    if region_filter is not None:
        regions_map = regions_map[regions_map.ADM1_AVF.apply(region_filter)]

    fig, ax = plt.subplots()
    mapping_utils.plot_frequency_map(regions_map, "ADM1_AVF", region_frequencies,
                                     label_position_columns=("ADM1_LX", "ADM1_LY"),
                                     legend_position=legend_position,
                                     callout_position_columns=("ADM1_CALLX", "ADM1_CALLY"),
                                     ax=ax)
    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()


def export_somalia_district_frequencies_map(district_frequencies, file_path, region_filter=None,
                                            legend_position="lower right"):
    """
    Exports a choropleth map of Somalia's regions, with each region shaded and labelled according to the given
    frequency for each region.

    :param district_frequencies: Dictionary of Somalia district code -> frequency count
    :type district_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    :param legend_position: Where on the map to draw the legend. For accepted values, see `loc` at
                            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
    :type legend_position: str
    """
    districts_map = mapping_utils.get_standard_geodata("somalia", "districts")
    if region_filter is not None:
        districts_map = districts_map[districts_map.ADM2_AVF.apply(region_filter)]

    fig, ax = plt.subplots()
    mapping_utils.plot_frequency_map(
        districts_map, "ADM2_AVF", district_frequencies, legend_position=legend_position, ax=ax
    )
    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()


def export_mogadishu_sub_district_frequencies_map(mogadishu_sub_district_frequencies, file_path, region_filter=None,
                                                  legend_position="lower right"):
    """
    Exports a choropleth map of Somalia's regions, with each region shaded and labelled according to the given
    frequency for each region.

    :param mogadishu_sub_district_frequencies: Dictionary of Mogadishu sub-district code -> frequency count
    :type mogadishu_sub_district_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    :param legend_position: Where on the map to draw the legend. For accepted values, see `loc` at
                            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
    :type legend_position: str
    """
    sub_districts_map = mapping_utils.get_standard_geodata("somalia", "mogadishu_sub_districts")
    if region_filter is not None:
        sub_districts_map = sub_districts_map[sub_districts_map.ADM3_AVF.apply(region_filter)]

    fig, ax = plt.subplots()
    mapping_utils.plot_frequency_map(sub_districts_map, "ADM3_AVF", mogadishu_sub_district_frequencies,
                                     label_position_columns=("ADM3_LX", "ADM3_LY"),
                                     legend_position=legend_position, ax=ax)
    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()
