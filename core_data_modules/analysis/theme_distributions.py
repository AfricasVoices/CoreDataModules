from collections import OrderedDict

from core_data_modules.analysis import analysis_utils
from core_data_modules.cleaners import Codes
from core_data_modules.data_models.code_scheme import CodeTypes


def _non_stop_codes(codes):
    return [code for code in codes if code.control_code != Codes.STOP]


def _normal_codes(codes):
    return [code for code in codes if code.code_type == CodeTypes.NORMAL]


def _make_breakdowns_dict(breakdown_configurations):
    breakdowns = OrderedDict()

    breakdowns["Total Participants"] = 0
    breakdowns["Total Participants %"] = None

    for config in breakdown_configurations:
        for code in _non_stop_codes(config.code_scheme.codes):
            breakdowns[f"{config.dataset_name}:{code.string_value}"] = 0
            breakdowns[f"{config.dataset_name}:{code.string_value} %"] = None

    return breakdowns


def _update_breakdowns(breakdowns, individual, breakdown_configurations):
    breakdowns["Total Participants"] += 1

    for config in breakdown_configurations:
        for code in _non_stop_codes(analysis_utils.get_codes_from_td(individual, config)):
            breakdowns[f"{config.dataset_name}:{code.string_value}"] += 1


def _compute_percentage_str(x, y):
    if y == 0:
        return "-"
    else:
        return str(round(x / y * 100, 1))


def _compute_breakdown_percentages(breakdowns, total_breakdowns, breakdown_configurations):
    breakdowns["Total Participants %"] = \
        _compute_percentage_str(breakdowns["Total Participants"], total_breakdowns["Total Participants"])

    for config in breakdown_configurations:
        for code in _non_stop_codes(config.code_scheme.codes):
            theme_name = f"{config.dataset_name}:{code.string_value}"
            breakdowns[f"{theme_name} %"] = \
                _compute_percentage_str(breakdowns[theme_name], total_breakdowns[theme_name])


def _compute_theme_distributions_for_dataset(individuals, consent_withdrawn_field, theme_config, breakdown_configurations):
    themes = OrderedDict()  # of theme_config dataset name -> theme -> (dict of breakdown code -> dict of count/%)

    themes["Total Relevant Participants"] = _make_breakdowns_dict(breakdown_configurations)
    for code in _non_stop_codes(theme_config.code_scheme.codes):
        themes[f"{theme_config.dataset_name}_{code.string_value}"] = _make_breakdowns_dict(breakdown_configurations)

    # Iterate over the individuals, increasing the counts as needed
    for ind in individuals:
        if analysis_utils.relevant(ind, consent_withdrawn_field, theme_config):
            _update_breakdowns(themes["Total Relevant Participants"], ind, breakdown_configurations)

        for code in analysis_utils.get_codes_from_td(ind, theme_config):
            _update_breakdowns(themes[f"{theme_config.dataset_name}_{code.string_value}"],
                               ind, breakdown_configurations)

    _compute_breakdown_percentages(
        themes["Total Relevant Participants"], themes["Total Relevant Participants"],
        breakdown_configurations
    )

    for code in _normal_codes(theme_config.code_scheme.codes):
        _compute_breakdown_percentages(
            themes[f"{theme_config.dataset_name}_{code.string_value}"], themes["Total Relevant Participants"],
            breakdown_configurations
        )

    return themes


def compute_theme_distributions(individuals, consent_withdrawn_field, theme_configurations, breakdown_configurations):
    theme_distributions = OrderedDict()  # of dataset_name -> theme ->

    individuals = analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, theme_configurations)

    # For each theme configuration, create a dict of theme dataset_name -> (dict of breakdown code -> count/%)
    for theme_config in theme_configurations:
        theme_distributions[theme_config.dataset_name] = _compute_theme_distributions_for_dataset(
            individuals, consent_withdrawn_field, theme_config, breakdown_configurations
        )

    return theme_distributions


def write_theme_distributions_csv(individuals, consent_withdrawn_field, theme_configurations, breakdown_configurations, f):
    theme_distributions = compute_theme_distributions(individuals, consent_withdrawn_field,
                                                      theme_configurations, breakdown_configurations)

    csv_data = []
    last_dataset_name = None
    for dataset_name, themes in theme_distributions.items():
        for theme, breakdowns in themes.items():
            row = {
                "Theme": theme,
                "Dataset": dataset_name if dataset_name != last_dataset_name else ""
            }
            row.update(breakdowns)
            csv_data.append(row)
            last_dataset_name = dataset_name

    headers = ["Dataset", "Theme"]
    headers.extend(_make_breakdowns_dict(breakdown_configurations).keys())

    analysis_utils.write_csv(
        csv_data,
        headers,
        f
    )
