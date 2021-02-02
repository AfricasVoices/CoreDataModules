import matplotlib.pyplot as plt

from core_data_modules.analysis.mapping import mapping_utils


def export_kenya_constituencies_map(constituency_frequencies, file_path):
    """
    Exports a choropleth map of Kenya's constituencies, with each constituency shaded according to the given frequency
    for each constituency.

    :param constituency_frequencies: Dictionary of Kenya constituency code -> frequency count
    :type constituency_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    """
    constituencies_map = mapping_utils.get_standard_geodata("kenya", "constituencies")
    lakes_map = mapping_utils.get_standard_geodata("kenya", "lakes")
    lakes_map = lakes_map[lakes_map.LAKE_AVF.isin({"lake_turkana", "lake_victoria"})]

    fig, ax = plt.subplots()

    # Draw the base map
    mapping_utils.plot_frequency_map(constituencies_map, "ADM2_AVF", constituency_frequencies, ax=ax)

    # Draw a zoomed inset map of Nairobi because the constituencies here are really small
    mapping_utils.plot_inset_frequency_map(
        constituencies_map, "ADM2_AVF", constituency_frequencies,
        inset_region=(36.62, -1.46, 37.12, -1.09), zoom=3, inset_position=(35.60, -2.95), ax=ax
    )

    # Draw Kenya's lakes
    mapping_utils.plot_water_bodies(lakes_map, ax=ax)

    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()


def export_kenya_counties_map(county_frequencies, file_path):
    """
    Exports a choropleth map of Kenya's counties, with each county shaded and labelled according to the given frequency
    for each county.

    :param county_frequencies: Dictionary of Kenya county code -> frequency count
    :type county_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    """
    counties_map = mapping_utils.get_standard_geodata("kenya", "counties")
    lakes_map = mapping_utils.get_standard_geodata("kenya", "lakes")
    lakes_map = lakes_map[lakes_map.LAKE_AVF.isin({"lake_turkana", "lake_victoria"})]

    fig, ax = plt.subplots()

    # Draw the base map
    mapping_utils.plot_frequency_map(counties_map, "ADM1_AVF", county_frequencies, ax=ax,
                                     # labels=labels,  TODO: Find out what this is
                                     label_position_columns=("ADM1_LX", "ADM1_LY"),
                                     callout_position_columns=("ADM1_CALLX", "ADM1_CALLY"))

    # Draw Kenya's lakes
    mapping_utils.plot_water_bodies(lakes_map, ax=ax)

    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()
