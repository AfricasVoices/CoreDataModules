from collections import OrderedDict

from core_data_modules.analysis import analysis_utils
from core_data_modules.cleaners import Codes


def _non_stop_codes(codes):
    return [code for code in codes if code.control_code != Codes.STOP]


def _make_survey_counts_dict(survey_configurations):
    survey_counts = OrderedDict()

    survey_counts["Total Participants"] = 0
    survey_counts["Total Participants %"] = None

    for config in survey_configurations:
        for code in _non_stop_codes(config.code_scheme.codes):
            survey_counts[f"{config.dataset_name}:{code.string_value}"] = 0
            survey_counts[f"{config.dataset_name}:{code.string_value} %"] = None

    return survey_counts


def _update_survey_counts_dict(survey_counts, individual, survey_configurations):
    for config in survey_configurations:
        for code in _non_stop_codes(analysis_utils.get_codes_from_td(individual, config)):
            survey_counts[f"{config.dataset_name}:{code.string_value}"] += 1


def _set_survey_counts_percentages(survey_counts, total_survey_counts, survey_configurations):
    pass


def compute_theme_distributions(individuals, consent_withdrawn_field, theme_configurations, survey_configurations):
    theme_distributions = OrderedDict()  # of TODO

    individuals = analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, theme_configurations)

    # For each theme configuration, create a dict of theme dataset_name -> (dict of survey code -> count/%)
    for theme_config in theme_configurations:
        themes = OrderedDict()
        theme_distributions[theme_config.dataset_name] = themes

        # For each code in the rqa code scheme, add an entry
        for code in _non_stop_codes(theme_config.code_scheme.codes):
            themes["Total Relevant Participants"] = 0
            themes[f"{theme_config.dataset_name}_{code.string_value}"] = _make_survey_counts_dict(survey_configurations)

        for ind in individuals:
            # If the individual is relevant to this rqa configuration, increase the total relevant count and
            # associated survey columns by 1.
            if analysis_utils.relevant(ind, consent_withdrawn_field, theme_config):
                themes["Total Relevant Participants"]["Total Participants"] += 1
                _update_survey_counts_dict(themes["Total Relevant Participants"], ind, survey_configurations)

            # For each theme in this rqa configuration, increase the theme's total count and associated survey columns
            # by 1.
            for code in analysis_utils.get_codes_from_td(ind, theme_config):
                theme_name = f"{theme_config.dataset_name}_{code.string_value}"
                themes[theme_name] += 1
                _update_survey_counts_dict(themes[theme_name], ind, survey_configurations)

    # TODO: Set percentages

    return theme_distributions
