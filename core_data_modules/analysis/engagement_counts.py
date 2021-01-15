from collections import OrderedDict

from core_data_modules.analysis import analysis_utils

engagement_counts_headers = [
    "Dataset",
    "Total Messages", "Total Messages with Opt-Ins", "Total Labelled Messages", "Total Relevant Messages",
    "Total Participants", "Total Participants with Opt-Ins", "Total Relevant Participants"
]


def compute_engagement_counts(messages, individuals, consent_withdrawn_field, analysis_configurations):
    engagement_counts = OrderedDict()  # of dataset name to counts

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
    analysis_utils.write_csv(
        compute_engagement_counts(messages, individuals, consent_withdrawn_field, analysis_configurations).values(),
        engagement_counts_headers,
        f
    )
