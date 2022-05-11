from collections import OrderedDict

from core_data_modules.analysis import analysis_utils
from core_data_modules.data_models import CodeTypes

_NUMBER_OF_INDIVIDUALS_HEADER = "Number of Individuals"


def _normal_codes(codes):
    """
    Filters a list of codes for those with code type CodeTypes.NORMAL.

    :param codes: Codes to filter.
    :type codes: list of core_data_modules.data_models.Code
    :return: All codes in `codes` which have code type CodeTypes.NORMAL.
    :rtype: list of core_data_modules.data_models.Code
    """
    return [code for code in codes if code.code_type == CodeTypes.NORMAL]


def compute_cross_tabs(individuals, consent_withdrawn_field, analysis_configuration_1, analysis_configuration_2):
    """
    Computes cross-tabs.

    :param individuals: Individuals to compute the cross-tabs for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configuration_1: Configuration for the first cross-tab variable.
    :type analysis_configuration_1: core_data_modules.analysis.AnalysisConfiguration
    :param analysis_configuration_2: Configuration for the second cross-tab variable.
    :type analysis_configuration_2: core_data_modules.analysis.AnalysisConfiguration
    :return: List of dictionaries containing (i) configuration 1 code string value, (ii) configuration 2 code string
             value, (iii) Number of individuals seen with this pair of codes, (iv) percentage distributions of
             each code in `analysis_configuration_2` within each `analysis_configuration_1`.
    :rtype: list of dict
    """
    # Store the counts in a dictionary of (config_1 code.string_value, config_2 code.string_value) -> (
    #   dict containing (a) pairs of string values, and (b) the number of individuals with this pair
    # )
    cross_tab_counts = OrderedDict()

    # Initialise the cross_tab_counts dict with all the possible combinations in the 2 given code schemes, with counts
    # initially set to 0.
    for code_1 in _normal_codes(analysis_configuration_1.code_scheme.codes):
        for code_2 in _normal_codes(analysis_configuration_2.code_scheme.codes):
            # Assign the count dict for this pair of codes
            # e.g. { "gender": "man", "age_category": "10_to_14", "Number of Individuals": 0 }
            cross_tab_counts[(code_1.string_value, code_2.string_value)] = {
                analysis_configuration_1.dataset_name: code_1.string_value,
                analysis_configuration_2.dataset_name: code_2.string_value,
                _NUMBER_OF_INDIVIDUALS_HEADER: 0
            }

    # Count up all the individuals in each category.
    individuals = analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field)
    for ind in individuals:
        config_1_normal_codes = _normal_codes(analysis_utils.get_codes_from_td(ind, analysis_configuration_1))
        config_2_normal_codes = _normal_codes(analysis_utils.get_codes_from_td(ind, analysis_configuration_2))

        # Cross-tab analysis only supports individuals which have at most 1 normal code for now.
        assert len(config_1_normal_codes) <= 1, config_1_normal_codes
        assert len(config_2_normal_codes) <= 1, config_2_normal_codes

        if len(config_1_normal_codes) == 0 or len(config_2_normal_codes) == 0:
            continue

        cross_tab_key = (config_1_normal_codes[0].string_value, config_2_normal_codes[0].string_value)
        cross_tab_counts[cross_tab_key][_NUMBER_OF_INDIVIDUALS_HEADER] += 1

    # Compute percentages
    for code_1 in _normal_codes(analysis_configuration_1.code_scheme.codes):
        # Count the total number of individuals with code_1
        code_1_total = 0
        for code_2 in _normal_codes(analysis_configuration_2.code_scheme.codes):
            cross_tab_key = (code_1.string_value, code_2.string_value)
            code_1_total += cross_tab_counts[cross_tab_key][_NUMBER_OF_INDIVIDUALS_HEADER]

        # For each code 2, compute the percentage occurrence of this code within the other code 2s for this code 1.
        # For example, compute the percentage distributions of gender for each age-range.
        for code_2 in _normal_codes(analysis_configuration_2.code_scheme.codes):
            cross_tab_key = (code_1.string_value, code_2.string_value)
            pair_count = cross_tab_counts[cross_tab_key][_NUMBER_OF_INDIVIDUALS_HEADER]
            percent_key = f"{analysis_configuration_2.dataset_name} / {analysis_configuration_1.dataset_name} (%)"
            cross_tab_counts[cross_tab_key][percent_key] = analysis_utils.compute_percentage_str(pair_count, code_1_total)

    # Convert the cross-tab counts to a csv-friendly list of dictionaries
    return list(cross_tab_counts.values())


def export_cross_tabs_csv(individuals, consent_withdrawn_field, analysis_configuration_1, analysis_configuration_2, f):
    """
    Computes cross-tabs and exports them to a file.

    :param individuals: Individuals to compute the cross-tabs for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configuration_1: Configuration for the first cross-tab variable.
    :type analysis_configuration_1: core_data_modules.analysis.AnalysisConfiguration
    :param analysis_configuration_2: Configuration for the second cross-tab variable.
    :type analysis_configuration_2: core_data_modules.analysis.AnalysisConfiguration
    :param f: File to write the cross_tabs CSV to.
    :type f: file-like
    """
    cross_tabs = compute_cross_tabs(
        individuals, consent_withdrawn_field, analysis_configuration_1, analysis_configuration_2
    )

    analysis_utils.write_csv(
        cross_tabs,
        list(cross_tabs[0].keys()),
        f
    )
