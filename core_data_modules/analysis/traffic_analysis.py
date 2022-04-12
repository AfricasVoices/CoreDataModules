from dateutil.parser import isoparse

from core_data_modules.analysis import analysis_utils
from core_data_modules.analysis.analysis_utils import compute_percentage_str


class TrafficLabel(object):
    def __init__(self, start_date, end_date, label):
        """
        :param start_date: Inclusive start date of the time-range for this label.
        :type start_date: datetime.datetime
        :param end_date: Exclusive end date of the time-range for this label.
        :type end_date: datetime.datetime
        :param label: Label to assign to this time-range.
        :type label: str
        """
        self.start_date = start_date
        self.end_date = end_date
        self.label = label


traffic_analysis_keys = [
    "Start Date", "End Date", "Label", "Messages with Opt-Ins", "Relevant Messages", "Relevant Messages (%)"
]


def compute_traffic_analysis(messages, consent_withdrawn_field, analysis_configurations, time_field, traffic_labels):
    """
    Computes the number of opt-in and relevant messages for the time ranges in the given traffic labels.

    :param messages: Messages to compute the engagement_counts for.
    :type messages: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each messages object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets/coded fields to check for opt-ins/relevance in
                                    the time ranges.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param time_field: Field in each messages object which records when the message was sent.
    :type time_field: str
    :param traffic_labels: Time ranges to search and labels to apply.
    :type traffic_labels: iterable of TrafficLabel
    :return: List of dictionaries containing the keys `traffic_analysis_keys`.
    :rtype: list of (dict of str -> str | int)
    """
    opt_in_messages = analysis_utils.filter_opt_ins(messages, consent_withdrawn_field)

    traffic_analysis = []
    for traffic_label in traffic_labels:
        opt_in_messages_in_time_range = [msg for msg in opt_in_messages if
                                         traffic_label.start_date <= isoparse(msg[time_field]) < traffic_label.end_date]

        messages_with_opt_ins = len(opt_in_messages_in_time_range)
        relevant_messages = len(analysis_utils.filter_relevant(
            opt_in_messages_in_time_range, consent_withdrawn_field, analysis_configurations)
        )

        traffic_analysis.append({
            "Start Date": traffic_label.start_date.isoformat(),
            "End Date": traffic_label.end_date.isoformat(),
            "Label": traffic_label.label,
            "Messages with Opt-Ins": messages_with_opt_ins,
            "Relevant Messages": relevant_messages,
            "Relevant Messages (%)": compute_percentage_str(relevant_messages, messages_with_opt_ins)
        })

    return traffic_analysis


def export_traffic_analysis_csv(messages, consent_withdrawn_field, analysis_configurations, time_field, traffic_labels,
                                f):
    """
    Computes the traffic_analysis and exports the results to a CSV.

    :param messages: Messages to compute the engagement_counts for.
    :type messages: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each messages object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets/coded fields to check for opt-ins/relevance in
                                    the time ranges.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param time_field: Field in each messages object which records when the message was sent.
    :type time_field: str
    :param traffic_labels: Time ranges to search and labels to apply.
    :type traffic_labels: iterable of TrafficLabel
    :param f: File to write the engagement_counts CSV to.
    :type f: file-like
    """
    analysis_utils.write_csv(
        compute_traffic_analysis(messages, consent_withdrawn_field, analysis_configurations, time_field, traffic_labels),
        traffic_analysis_keys,
        f
    )
