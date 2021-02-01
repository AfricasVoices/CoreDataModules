from collections import OrderedDict

from core_data_modules.analysis import analysis_utils
from core_data_modules.cleaners import Codes
from core_data_modules.data_models.code_scheme import CodeTypes


def _non_stop_codes(codes):
    """
    Filters a list of codes for those that do not have control code Codes.STOP.

    :param codes: Codes to filter.
    :type codes: list of core_data_modules.data_models.Code
    :return: All codes in `codes` except those with control code Codes.STOP.
    :rtype: list of core_data_modules.data_models.Code
    """
    return [code for code in codes if code.control_code != Codes.STOP]


def _normal_codes(codes):
    """
    Filters a list of codes for those with code type CodeTypes.NORMAL.

    :param codes: Codes to filter.
    :type codes: list of core_data_modules.data_models.Code
    :return: All codes in `codes` which have code type CodeTypes.NORMAL.
    :rtype: list of core_data_modules.data_models.Code
    """
    return [code for code in codes if code.code_type == CodeTypes.NORMAL]


def _make_breakdowns_dict(breakdown_configurations):
    """
    Constructs a dictionary to store breakdown counts and percentages for the given breakdown_configurations.

    The returned dictionary will contain the following:
     - "Total Participants": 0
     - "Total Participants %": None (to set this later see `theme_distributions._compute_breakdown_percentages`.
     - For each code in each breakdown_configuration:
       - "{breakdown_configuration.dataset_name}:{code.string_value}": 0
       - "{breakdown_configuration.dataset_name}:{code.string_value} %": None
       For example, "age:20": 0, "age:20 %": None

    :param breakdown_configurations: Configuration for the breakdowns.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Initialised breakdowns dictionary.
    :rtype: dict of str -> (int | None)
    """
    breakdowns = OrderedDict()

    breakdowns["Total Participants"] = 0
    breakdowns["Total Participants %"] = None

    for config in breakdown_configurations:
        for code in _non_stop_codes(config.code_scheme.codes):
            breakdowns[f"{config.dataset_name}:{code.string_value}"] = 0
            breakdowns[f"{config.dataset_name}:{code.string_value} %"] = None

    return breakdowns


def _increment_breakdowns(breakdowns, individual, breakdown_configurations):
    """
    Increments the non-percentage entries of a breakdowns dictionary in-place based on the codes present in the given
    individual.

    The "Total Participants" entry in `breakdowns` will always be incremented by 1.
    The remaining entries will be incremented by 1 if the code is present in the `individual`.

    For efficiency reasons, the percentage fields are not touched so may go out of sync without a subsequent call to
    _compute_breakdown_percentages.

    :param breakdowns: Breakdowns dictionary to update.
    :type breakdowns: dict of str -> (int | str | None)
    :param individual: Individual to use to update the breakdowns dictionary.
    :type individual: core_data_modules.traced_data.TracedData
    :param breakdown_configurations: Configuration for the breakdowns.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    """
    breakdowns["Total Participants"] += 1

    for config in breakdown_configurations:
        for code in _non_stop_codes(analysis_utils.get_codes_from_td(individual, config)):
            breakdowns[f"{config.dataset_name}:{code.string_value}"] += 1


def _compute_breakdown_percentages(breakdowns, total_breakdowns, breakdown_configurations):
    """
    Sets the percentage fields in a breakdowns dict, in-place.

    :param breakdowns: Breakdowns dictionary to update.
    :type breakdowns: dict of str -> (str | int | None)
    :param total_breakdowns: Breakdowns dictionary containing the totals to compute the percentages out of.
    :type total_breakdowns: dict of str -> (str | int | None)
    :param breakdown_configurations: Configuration for the breakdowns.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    """
    breakdowns["Total Participants %"] = \
        analysis_utils.compute_percentage_str(breakdowns["Total Participants"], total_breakdowns["Total Participants"])

    for config in breakdown_configurations:
        for code in _non_stop_codes(config.code_scheme.codes):
            theme_name = f"{config.dataset_name}:{code.string_value}"
            breakdowns[f"{theme_name} %"] = \
                analysis_utils.compute_percentage_str(breakdowns[theme_name], total_breakdowns[theme_name])


def _compute_theme_distributions_for_theme_configuration(individuals, consent_withdrawn_field, theme_configuration,
                                                         breakdown_configurations):
    """
    Computes the theme_distributions for a list of individuals, for a single theme_configuration.

    Returns a dictionary of theme -> breakdowns.

    :param individuals: Individuals to compute the theme_distributions for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param theme_configuration: Configuration for the themes. Each configuration should contain:
                                - dataset_name.
                                - code_scheme. This will be used to index the returned dict (the "theme" above).
                                  Themes are formatted as
                                  {theme_configuration.dataset_name}_{code.string_value} for each code in the
                                  code_scheme.
    :type theme_configuration: core_data_modules.analysis.AnalysisConfiguration
    :param breakdown_configurations: Configuration for the breakdowns dict.
                                     For details, see `theme_distributions._make_breakdowns_dict`.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Dictionary of theme -> breakdowns.
    :rtype: dict of str -> (str -> (int | str))
    """
    themes = OrderedDict()  # of theme -> breakdowns

    # Create initial breakdowns dicts for 'Total Participants' and for each theme in this theme_configuration.
    themes["Total Relevant Participants"] = _make_breakdowns_dict(breakdown_configurations)
    for code in _non_stop_codes(theme_configuration.code_scheme.codes):
        themes[code.string_value] = \
            _make_breakdowns_dict(breakdown_configurations)

    # Iterate over the individuals, incrementing:
    #  - The Total Relevant Participants, if the individual is considered relevant under this theme_configuration.
    #  - The breakdowns dicts for each theme that this individual is labelled to have.
    for ind in individuals:
        if analysis_utils.relevant(ind, consent_withdrawn_field, theme_configuration):
            _increment_breakdowns(themes["Total Relevant Participants"], ind, breakdown_configurations)

        for code in analysis_utils.get_codes_from_td(ind, theme_configuration):
            _increment_breakdowns(themes[code.string_value],
                                  ind, breakdown_configurations)

    # Compute the percentages in each breakdown dict, for the Total Relevant Participants and for each theme,
    # relative to the Total Relevant Participants.
    _compute_breakdown_percentages(
        themes["Total Relevant Participants"], themes["Total Relevant Participants"],
        breakdown_configurations
    )
    for code in _normal_codes(theme_configuration.code_scheme.codes):
        _compute_breakdown_percentages(
            themes[code.string_value], themes["Total Relevant Participants"],
            breakdown_configurations
        )

    return themes


def compute_theme_distributions(individuals, consent_withdrawn_field, theme_configurations, breakdown_configurations):
    """
    Computes the theme distributions for a list of individuals.

    Returns a dictionary of theme dataset_name -> theme -> breakdowns.

    :param individuals: Individuals to compute the theme_distributions for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param theme_configurations: Configuration for the themes. Each configuration should contain:
                                  - dataset_name. This will be used to index the returned theme_distributions dict
                                    (the "theme dataset_name" above).
                                  - code_scheme. This will be used to index each themes dictionary in the returned
                                    theme_distributions dict (the "theme" above). Themes are formatted as
                                    {theme_configuration.dataset_name}_{code.string_value} for each code in the
                                    code_scheme.
    :type theme_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param breakdown_configurations: Configuration for the breakdowns dict.
                                     For details, see `theme_distributions._make_breakdowns_dict`.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Dictionary of theme dataset_name -> theme -> breakdowns.
    :rtype: dict of str -> str -> (str -> (int | str))
    """
    individuals = analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, theme_configurations)

    theme_distributions = OrderedDict()  # of dataset_name -> theme -> breakdowns
    for theme_config in theme_configurations:
        theme_distributions[theme_config.dataset_name] = _compute_theme_distributions_for_theme_configuration(
            individuals, consent_withdrawn_field, theme_config, breakdown_configurations
        )

    return theme_distributions


def export_theme_distributions_csv(individuals, consent_withdrawn_field,
                                   theme_configurations, breakdown_configurations, f):
    """
    Computes the theme_distributions and exports them to a CSV.

    The CSV will contain the headers:
     - Dataset, set to the dataset_name in each of the `theme_configurations`, de-duplicated for clarity).
     - Theme, set to {dataset_name}_{code.string_value}, for each code in each theme_configuration.
     - Total Participants
     - Total Participants %
    and raw total and % headers for each scheme and code in the `breakdown_configurations`.

    :param individuals: Individuals to compute the theme_distributions for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param theme_configurations: Configuration for the themes. Each configuration should contain:
                                  - dataset_name. This will be used to index the returned theme_distributions dict
                                    (the "theme dataset_name" above).
                                  - code_scheme. This will be used to index each themes dictionary in the returned
                                    theme_distributions dict (the "theme" above). Themes are formatted as
                                    {theme_configuration.dataset_name}_{code.string_value} for each code in the
                                    code_scheme.
    :type theme_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param breakdown_configurations: Configuration for the breakdowns dict.
                                     For details, see `theme_distributions._make_breakdowns_dict`.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param f: File to write the theme_distributions CSV to.
    :type f: file-like
    """
    theme_distributions = compute_theme_distributions(individuals, consent_withdrawn_field,
                                                      theme_configurations, breakdown_configurations)

    # Denormalize the theme_distributions into a flat array of dicts that can be written to disk.
    csv_data = []
    last_dataset_name = None
    for dataset_name, themes in theme_distributions.items():
        for theme, breakdowns in themes.items():
            row = {
                "Dataset": dataset_name if dataset_name != last_dataset_name else "",
                "Theme": theme
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
