from collections import OrderedDict

from core_data_modules.analysis import analysis_utils
from core_data_modules.cleaners import Codes
from core_data_modules.data_models.code_scheme import CodeTypes


def _non_stop_codes(codes):
    return [code for code in codes if code.control_code != Codes.STOP]


def _normal_codes(codes):
    return [code for code in codes if code.code_type == CodeTypes.NORMAL]


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
    survey_counts["Total Participants"] += 1

    for config in survey_configurations:
        for code in _non_stop_codes(analysis_utils.get_codes_from_td(individual, config)):
            survey_counts[f"{config.dataset_name}:{code.string_value}"] += 1


def _compute_percentage_str(x, y):
    if y == 0:
        return "-"
    else:
        return str(round(x / y * 100, 1))


def _set_survey_counts_percentages(survey_counts, total_survey_counts, survey_configurations):
    survey_counts["Total Participants %"] = \
        _compute_percentage_str(survey_counts["Total Participants"], total_survey_counts["Total Participants"])

    for config in survey_configurations:
        for code in _non_stop_codes(config.code_scheme.codes):
            theme_name = f"{config.dataset_name}:{code.string_value}"
            survey_counts[f"{theme_name} %"] = \
                _compute_percentage_str(survey_counts[theme_name], total_survey_counts[theme_name])


def _compute_theme_distributions_for_rqa(individuals, consent_withdrawn_field, theme_config, survey_configurations):
    themes = OrderedDict()  # of rqa code -> (dict of survey_code -> dict of count/%)

    # For each code in the rqa code scheme, add an entry
    themes["Total Relevant Participants"] = _make_survey_counts_dict(survey_configurations)
    for code in _non_stop_codes(theme_config.code_scheme.codes):
        themes[f"{theme_config.dataset_name}_{code.string_value}"] = _make_survey_counts_dict(survey_configurations)

    # Iterate over the individuals, increasing the counts as needed
    for ind in individuals:
        if analysis_utils.relevant(ind, consent_withdrawn_field, theme_config):
            _update_survey_counts_dict(themes["Total Relevant Participants"], ind, survey_configurations)

        for code in analysis_utils.get_codes_from_td(ind, theme_config):
            _update_survey_counts_dict(themes[f"{theme_config.dataset_name}_{code.string_value}"],
                                       ind, survey_configurations)

    _set_survey_counts_percentages(
        themes["Total Relevant Participants"], themes["Total Relevant Participants"],
        survey_configurations
    )

    for code in _normal_codes(theme_config.code_scheme.codes):
        _set_survey_counts_percentages(
            themes[f"{theme_config.dataset_name}_{code.string_value}"], themes["Total Relevant Participants"],
            survey_configurations
        )

    return themes


def compute_theme_distributions(individuals, consent_withdrawn_field, theme_configurations, survey_configurations):
    theme_distributions = OrderedDict()  # of dataset_name -> theme ->

    individuals = analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, theme_configurations)

    # For each theme configuration, create a dict of theme dataset_name -> (dict of survey code -> count/%)
    for theme_config in theme_configurations:
        theme_distributions[theme_config.dataset_name] = _compute_theme_distributions_for_rqa(
            individuals, consent_withdrawn_field, theme_config, survey_configurations
        )

    return theme_distributions


def write_theme_distributions_csv(individuals, consent_withdrawn_field, theme_configurations, survey_configurations, f):
    theme_distributions = compute_theme_distributions(individuals, consent_withdrawn_field,
                                                      theme_configurations, survey_configurations)

    csv_data = []
    last_dataset_name = None
    for dataset_name, themes in theme_distributions.items():
        for theme, survey_counts in themes.items():
            row = {
                "Theme": theme,
                "Dataset": dataset_name if dataset_name != last_dataset_name else ""
            }
            row.update(survey_counts)
            csv_data.append(row)
            last_dataset_name = dataset_name

    headers = ["Dataset", "Theme"]
    headers.extend(_make_survey_counts_dict(survey_configurations).keys())

    analysis_utils.write_csv(
        csv_data,
        headers,
        f
    )
