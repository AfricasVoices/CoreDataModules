import random
import sys
from collections import OrderedDict

from core_data_modules.analysis import analysis_utils

sample_messages_keys = ["Episode", "Code Scheme", "Code", "Message"]


def _filter_codes_by_ids(codes, code_ids=None):
    if code_ids is None:
        return codes

    return [code for code in codes if code.code_id in code_ids]


def compute_sample_messages(messages, consent_withdrawn_field, analysis_configurations,
                            filter_code_ids=None, limit_per_code=sys.maxsize):
    """
    Exports sample messages with each code in the code schemes in the given analysis_configurations.

    :param messages: Objects to sample the messages from.
    :type messages: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each messages object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets to include in the sample_messages.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param filter_code_ids: The code ids to sample messages for, or None. If None, exports sample messages for all
                            code ids.
    :type filter_code_ids: list of str | None
    :param limit_per_code: The maximum number of sample messages to export per code.
                           Defaults to sys.maxsize, i.e. to no practical limit.
    :type limit_per_code: int
    :return: List of dictionaries with keys `sample_messages_keys`.
    :rtype: list of dict
    """
    samples = []   # of dict with keys `sample_messages_keys`.

    for config in analysis_configurations:
        # Iterate over the labelled messages, filling out code_to_messages with the full list of messages labelled
        # with each code
        code_to_messages = OrderedDict()  # of code.string_value -> list of raw message strings
        for code in _filter_codes_by_ids(config.code_scheme.codes, filter_code_ids):
            code_to_messages[code.string_value] = []

        for msg in analysis_utils.filter_partially_labelled(messages, consent_withdrawn_field, [config]):
            msg_codes = analysis_utils.get_codes_from_td(msg, config)
            for code in _filter_codes_by_ids(msg_codes, filter_code_ids):
                code_to_messages[code.string_value].append(msg[config.raw_field])

        # For each code, export up to the `limit_per_code` number of sample messages
        for code_string_value in code_to_messages:
            sample_size = min(limit_per_code, len(code_to_messages[code_string_value]))
            sample_messages = random.sample(code_to_messages[code_string_value], sample_size)

            for msg in sample_messages:
                samples.append({
                    "Episode": config.raw_field,
                    "Code Scheme": config.code_scheme.name,
                    "Code": code_string_value,
                    "Message": msg
                })

    return samples


def export_sample_messages_csv(messages, consent_withdrawn_field, analysis_configurations, f,
                               filter_code_ids=None, limit_per_code=sys.maxsize):
    """
    Computes the sample messages and exports them to a CSV.

    :param messages: Objects to sample the messages from.
    :type messages: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each messages object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param analysis_configurations: Configurations for the datasets to include in the sample_messages.
    :type analysis_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param f: File to write the sample_messages CSV to.
    :type f: file-like
    :param filter_code_ids: The code ids to sample messages for, or None. If None, exports sample messages for all
                            code ids.
    :type filter_code_ids: list of str | None
    :param limit_per_code: The maximum number of sample messages to export per code.
                           Defaults to sys.maxsize, i.e. to no practical limit.
    :type limit_per_code: int
    """
    analysis_utils.write_csv(
        compute_sample_messages(messages, consent_withdrawn_field, analysis_configurations,
                                filter_code_ids, limit_per_code),
        sample_messages_keys,
        f
    )
