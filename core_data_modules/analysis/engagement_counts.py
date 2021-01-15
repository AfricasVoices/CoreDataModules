from collections import OrderedDict

from core_data_modules.analysis import analysis_utils

engagement_counts_keys = [
    "Dataset",
    "Total Messages", "Total Messages with Opt-Ins", "Total Labelled Messages", "Total Relevant Messages",
    "Total Participants", "Total Participants with Opt-Ins", "Total Relevant Participants"
]


def compute_engagement_counts(messages, individuals, consent_withdrawn_field, analysis_configurations):
    """
    Computes the engagement counts for a list of messages and individuals.

    Returns a dictionary of dataset_name | "Total" -> dict with keys `engagement_counts_keys`.
    For definitions of each of the terms used here ("Opt-Ins", "Labelled", etc.), see the relevant function in
    `core_data_modules.analysis.analysis_utils`.

    :param messages: Messages to compute the engagement_counts for.
    :type messages: iterable of core_data_modules.traced_data.TracedData
    :param individuals: Individuals to compute the engagement_counts for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each messages/individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets/coded fields to include in the engagement_counts.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Dictionary of dataset_name | "Total" -> dict with keys `engagement_counts_keys`.
    :rtype: OrderedDict of str -> dict
    """
    engagement_counts = OrderedDict()  # of dataset_name -> dict with keys `engagement_counts_keys`

    for config in analysis_configurations:
        engagement_counts[config.dataset_name] = OrderedDict({
            "Dataset": config.dataset_name,

            "Total Messages": "-", # Can't report this for individual weeks because the data has been overwritten with "STOP"
            "Total Messages with Opt-Ins": len(analysis_utils.filter_opt_ins(messages, consent_withdrawn_field, [config])),
            "Total Labelled Messages": len(analysis_utils.filter_fully_labelled(messages, consent_withdrawn_field, [config])),
            "Total Relevant Messages": len(analysis_utils.filter_relevant(messages, consent_withdrawn_field, [config])),

            "Total Participants": "-",
            "Total Participants with Opt-Ins": len(analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, [config])),
            "Total Relevant Participants": len(analysis_utils.filter_relevant(individuals, consent_withdrawn_field, [config]))
        })

    engagement_counts["Total"] = OrderedDict({
        "Dataset": "Total",

        "Total Messages": len(messages),
        "Total Messages with Opt-Ins": len(analysis_utils.filter_opt_ins(messages, consent_withdrawn_field, analysis_configurations)),
        "Total Labelled Messages": len(analysis_utils.filter_fully_labelled(messages, consent_withdrawn_field, analysis_configurations)),
        "Total Relevant Messages": len(analysis_utils.filter_relevant(messages, consent_withdrawn_field, analysis_configurations)),

        "Total Participants": len(individuals),
        "Total Participants with Opt-Ins": len(analysis_utils.filter_opt_ins(individuals, consent_withdrawn_field, analysis_configurations)),
        "Total Relevant Participants": len(analysis_utils.filter_relevant(individuals, consent_withdrawn_field, analysis_configurations))
    })

    return engagement_counts


def write_engagement_counts_csv(messages, individuals, consent_withdrawn_field, analysis_configurations, f):
    """
    Computes the engagement_counts and exports them to a CSV.

    :param messages: Messages to compute the engagement_counts for.
    :type messages: iterable of core_data_modules.traced_data.TracedData
    :param individuals: Individuals to compute the engagement_counts for.
    :type individuals: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each messages/individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets/coded fields to include in the engagement_counts.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Dictionary of dataset_name | "Total" -> dict with keys `engagement_counts_keys`.
    :rtype: OrderedDict of str -> dict
    :param f: File to write the engagement_counts CSV to.
    :type f: file-like
    """
    analysis_utils.write_csv(
        compute_engagement_counts(messages, individuals, consent_withdrawn_field, analysis_configurations).values(),
        engagement_counts_keys,
        f
    )
