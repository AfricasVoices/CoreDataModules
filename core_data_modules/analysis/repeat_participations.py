from collections import OrderedDict

from core_data_modules.analysis import analysis_utils

repeat_participations_keys = [
    "Number of Episodes Participated In", "Number of Participants with Opt-Ins", "% of Participants with Opt-Ins"
]


def compute_repeat_participations(individuals, consent_withdrawn_field, analysis_configurations):
    """
    Computes the repeat participations for a list of individuals.

    Returns an OrderedDict of the number of episodes participated in to a dict containing the number of opt-in
    individuals who participated in exactly that number of episodes, and that number as a percentage of the total number
    of opting-in individuals.

    :param individuals: Individuals to compute the repeat participations for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets/coded fields to include in the engagement_counts.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Dictionary of number of episodes participated in -> dict with keys `repeat_participations_keys`.
    :rtype: OrderedDict of str -> dict
    """
    repeat_participations = OrderedDict()  # of number of episodes participated in -> dict with keys `repeat_participations_keys`

    for i in range(1, len(analysis_configurations) + 1):
        repeat_participations[i] = {
            "Number of Episodes Participated In": i,
            "Number of Participants with Opt-Ins": 0,
            "% of Participants with Opt-Ins": None
        }

    # Compute the number of individuals who participated each of 1 to (number of analysis_configurations) times.
    # An individual is considered to have 'participated' if they are an opt-in to an analysis_configuration.
    opt_in_individuals = analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, analysis_configurations)
    for ind in opt_in_individuals:
        episodes_participated = 0
        for config in analysis_configurations:
            if analysis_utils.opt_in(ind, consent_withdrawn_field, config):
                episodes_participated += 1
        assert episodes_participated != 0, f"Found an individual with no participation in any episode: {ind.items()}"
        repeat_participations[episodes_participated]["Number of Participants with Opt-Ins"] += 1

    # Compute the percentage of individuals who participated each possible number of times, out of the total number
    # of individuals who opted-in.
    for rp in repeat_participations.values():
        rp["% of Participants with Opt-Ins"] = \
            analysis_utils.compute_percentage_str(rp["Number of Participants with Opt-Ins"], len(opt_in_individuals))

    return repeat_participations


def export_repeat_participations_csv(individuals, consent_withdrawn_field, analysis_configurations, f):
    """
    Computes the repeat_participations and exports them to a CSV.

    :param individuals: Individuals to compute the repeat participations for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets/coded fields to include in the engagement_counts.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param f: File to write the engagement_counts CSV to.
    :type f: file-like
    """
    analysis_utils.write_csv(
        compute_repeat_participations(individuals, consent_withdrawn_field, analysis_configurations),
        repeat_participations_keys,
        f
    )
