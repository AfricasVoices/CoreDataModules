from core_data_modules.analysis import theme_distributions, analysis_utils
from core_data_modules.data_models.code_scheme import CodeTypes
from core_data_modules.logging import Logger
from core_data_modules.util import IOUtils

log = Logger(__name__)


def _normal_codes(codes):
    """
    Filters a list of codes for those with code type CodeTypes.NORMAL.

    :param codes: Codes to filter.
    :type codes: list of core_data_modules.data_models.Code
    :return: All codes in `codes` which have code type CodeTypes.NORMAL.
    :rtype: list of core_data_modules.data_models.Code
    """
    return [code for code in codes if code.code_type == CodeTypes.NORMAL]


def export_participation_maps(individuals, consent_withdrawn_field, theme_configurations, admin_region_configuration,
                              mapper, file_prefix, export_by_theme=True):
    """
    Computes and exports a map showing participation by administrative region.

    Optionally exports maps showing the participation broken down by theme.

    :param individuals: Individuals to export participation maps for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param theme_configurations: Configuration for the theme datasets.
    :type theme_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param admin_region_configuration: Configuration for the administrative region labels, used to count the engagement
                                       by admin region for each map.
    :type admin_region_configuration: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param mapper: A function which, given participation frequencies and a file name to export to, renders a map
                   of those frequencies to disk. For standard maps, see the mapper functions provided in
                   `core_data_modules.analysis.mapping`.
    :type mapper: func of (dict of str -> int, str) -> void
    :param file_prefix: The prefix of the path to write the files to, e.g. "/data/maps/mogadishu_"
    :type file_prefix: str
    :param export_by_theme: Whether to export a map of participation for each theme.
    :type export_by_theme: bool
    """
    IOUtils.ensure_dirs_exist_for_file(file_prefix)

    # Export a map showing the total participations
    log.info(f"Exporting map to '{file_prefix}total_participants.png'...")
    region_distributions = theme_distributions.compute_theme_distributions(
        analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, theme_configurations),
        consent_withdrawn_field,
        [admin_region_configuration],
        []
    )[admin_region_configuration.dataset_name]

    total_frequencies = dict()
    for region_code in _normal_codes(admin_region_configuration.code_scheme.codes):
        total_frequencies[region_code.string_value] = region_distributions[region_code.string_value]["Total Participants"]

    mapper(total_frequencies, f"{file_prefix}total_participants.png")

    if not export_by_theme:
        return

    # For each theme_configuration, export:
    #  1. A map showing the totals for individuals relevant to that episode.
    #  2. A map showing the totals for each theme
    distributions = theme_distributions.compute_theme_distributions(
        individuals, consent_withdrawn_field,
        theme_configurations,
        [admin_region_configuration]
    )

    for config in theme_configurations:
        map_index = 1
        log.info(f"Exporting map to '{file_prefix}{config.dataset_name}_{map_index}_total_relevant.png'...")
        config_total_frequencies = dict()
        for region_code in _normal_codes(admin_region_configuration.code_scheme.codes):
            config_total_frequencies[region_code.string_value] = distributions[config.dataset_name][
                "Total Relevant Participants"][f"{admin_region_configuration.dataset_name}:{region_code.string_value}"]

        mapper(config_total_frequencies, f"{file_prefix}{config.dataset_name}_{map_index}_total_relevant.png")

        for theme in _normal_codes(config.code_scheme.codes):
            map_index += 1
            log.info(f"Exporting map to '{file_prefix}{config.dataset_name}_{map_index}_{theme.string_value}.png'...")
            theme_frequencies = dict()
            for region_code in _normal_codes(admin_region_configuration.code_scheme.codes):
                theme_frequencies[region_code.string_value] = distributions[config.dataset_name][theme.string_value][
                    f"{admin_region_configuration.dataset_name}:{region_code.string_value}"]

            mapper(theme_frequencies, f"{file_prefix}{config.dataset_name}_{map_index}_{theme.string_value}.png")
