import matplotlib.pyplot as plt

from core_data_modules.analysis.mapping import mapping_utils


def export_somalia_region_frequencies_map(region_frequencies, file_path):
    """
    Exports a choropleth map of Somalia's regions, with each region shaded and labelled according to the given
    frequency for each region.

    :param region_frequencies: Dictionary of Somalia region code -> frequency count
    :type region_frequencies: dict of str -> int
    :param file_path: Path to write the generated map to.
    :type file_path: str
    """
    regions_map = mapping_utils.get_standard_geodata("somalia", "regions")

    fig, ax = plt.subplots()
    mapping_utils.plot_frequency_map(regions_map, "ADM1_AVF", region_frequencies,
                                     label_position_columns=("ADM1_LX", "ADM1_LY"),
                                     callout_position_columns=("ADM1_CALLX", "ADM1_CALLY"),
                                     ax=ax)
    plt.savefig(file_path, dpi=1200, bbox_inches="tight")
    plt.close()
