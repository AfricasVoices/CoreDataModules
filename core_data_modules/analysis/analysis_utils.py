from core_data_modules.cleaners import Codes
from core_data_modules.data_models.code_scheme import CodeTypes


class AnalysisConfiguration(object):
    def __init__(self, dataset_name, coded_field, code_scheme):
        self.dataset_name = dataset_name
        self.coded_field = coded_field
        self.code_scheme = code_scheme


def get_codes_from_td(td, analysis_configuration):
    coded_field = analysis_configuration.coded_field

    if coded_field not in td:
        return []

    if type(td[coded_field]) == list:
        labels = td[coded_field]
    else:
        labels = [td[coded_field]]

    return [analysis_configuration.code_scheme.get_code_with_code_id(label["CodeID"]) for label in labels]


def responded(td, analysis_configuration):
    codes = get_codes_from_td(td, analysis_configuration)
    assert len(codes) >= 1
    if len(codes) > 1:
        # If there is an NA or NS code, there shouldn't be any other codes present.
        for code in codes:
            assert code.control_code != Codes.TRUE_MISSING and code.control_code != Codes.SKIPPED
        return True
    return codes[0].control_code != Codes.TRUE_MISSING and codes[0].control_code != Codes.SKIPPED


def withdrew_consent(td, consent_withdrawn_key):
    """
    Returns whether the given TracedData object represents someone who withdrew their consent to have their data
    analysed.

    :param td: TracedData to check.
    :type td: TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :return: Whether consent was withdrawn.
    :rtype: bool
    """
    return td[consent_withdrawn_key] == Codes.TRUE


def opt_in(td, consent_withdrawn_key, analysis_configuration):
    """
    Returns whether the given TracedData object contains a response to the given coding_plan.

    A response is any field that hasn't been labelled with either TRUE_MISSING or SKIPPED.
    Returns False for participants who withdrew their consent to have their data analysed.

    :param td: TracedData to check.
    :type td: TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param coding_plan: A coding plan specifying the field names to look up in `td`, and the code scheme to use
                        to interpret those values.
    :type coding_plan: src.lib.pipeline_configuration.CodingPlan
    :return: Whether `td` contains a response to `coding_plan` and did not withdraw consent.
    :rtype: bool
    """
    if withdrew_consent(td, consent_withdrawn_key):
        return False

    return responded(td, analysis_configuration)


def labelled(td, consent_withdrawn_key, analysis_configuration):
    """
    Returns whether the given TracedData object has been labelled under the given coding_plan.

    An object is considered labelled if all of the following hold:
     - Consent was not withdrawn.
     - A response was received (see `AnalysisUtils.responded` for the definition of this).
     - The response has been assigned at least one label under each coding configuration.
     - None of the assigned labels have the control code NOT_REVIEWED.

    :param td: TracedData to check.
    :type td: TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param coding_plan: A coding plan specifying the field names to look up in `td`, and the code scheme to use
                        to interpret those values.
    :type coding_plan: src.lib.pipeline_configuration.CodingPlan
    :return: Whether `td` contains a labelled response to `coding_plan` and did not withdraw consent.
    :rtype: bool
    """
    if not responded(td, analysis_configuration):
        return False

    codes = get_codes_from_td(td, analysis_configuration)
    if len(codes) == 0:
        return False
    for code in codes:
        if code.control_code == Codes.NOT_REVIEWED:
            return False

    return True


def relevant(td, consent_withdrawn_key, analysis_configuration):
    """
    Returns whether the given TracedData object contains a relevant response to the given coding_plan.

    A response is considered relevant if it is labelled with a normal code under any of its coding configurations.
    Returns False for participants who withdrew their consent to have their data analysed.

    :param td: TracedData to check.
    :type td: TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param coding_plan: A coding plan specifying the field names to look up in `td`, and the code scheme to use
                        to interpret those values.
    :type coding_plan: src.lib.pipeline_configuration.CodingPlan
    :return: Whether `td` contains a relevant response to `coding_plan`.
    :rtype: bool
    """
    if withdrew_consent(td, consent_withdrawn_key):
        return False

    if not labelled(td, consent_withdrawn_key, analysis_configuration):
        return False

    codes = get_codes_from_td(td, analysis_configuration)
    for code in codes:
        if code.code_type == CodeTypes.NORMAL:
            return True

    return False
#
# @classmethod
# def filter_responded(cls, data, coding_plans):
#     """
#     Filters a list of message or participant data for objects that responded to at least one of the given coding
#     plans.
#
#     For the definition of "responded", see `AnalysisUtils.responded`
#
#     :param data: Message or participant data to filter.
#     :type data: TracedData iterable
#     :param coding_plans: Coding plans specifying the fields in each TracedData object in `data` to look up.
#     :type coding_plans: list of src.lib.pipeline_configuration.CodingPlan
#     :return: data, filtered for only the objects that responded to at least one of the coding plans.
#     :rtype: list of TracedData
#     """
#     responded = []
#     for td in data:
#         for plan in coding_plans:
#             if cls.responded(td, plan):
#                 responded.append(td)
#                 break
#     return responded


def filter_opt_ins(data, consent_withdrawn_key, analysis_configurations):
    """
    Filters a list of message or participant data for objects that opted-in and contained a response to at least
    one of the given coding plans.

    For the definition of "opted-in", see `AnalysisUtils.opt_in`

    :param data: Message or participant data to filter.
    :type data: TracedData iterable
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param coding_plans: Coding plans specifying the fields in each TracedData object in `data` to look up.
    :type coding_plans: list of src.lib.pipeline_configuration.CodingPlan
    :return: data, filtered for only the objects that opted-in and responded to at least one of the coding plans.
    :rtype: list of TracedData
    """
    opt_ins = []
    for td in data:
        for config in analysis_configurations:
            if opt_in(td, consent_withdrawn_key, config):
                opt_ins.append(td)
                break
    return opt_ins


# @classmethod
# def filter_partially_labelled(cls, data, consent_withdrawn_key, coding_plans):
#     """
#     Filters a list of message or participant data for objects that opted-in and are fully labelled under at least
#     one of the given coding plans.
#
#     For the definition of "labelled", see `AnalysisUtils.labelled`
#
#     :param data: Message or participant data to filter.
#     :type data: TracedData iterable
#     :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
#     :type consent_withdrawn_key: str
#     :param coding_plans: Coding plans specifying the fields in each TracedData object in `data` to look up.
#     :type coding_plans: list of src.lib.pipeline_configuration.CodingPlan
#     :return: `data`, filtered for only the objects that opted-in and are labelled under at least one of the coding
#              plans.
#     :rtype: list of TracedData
#     """
#     labelled = []
#     for td in data:
#         for plan in coding_plans:
#             if cls.labelled(td, consent_withdrawn_key, plan):
#                 labelled.append(td)
#                 break
#     return labelled

def filter_fully_labelled(data, consent_withdrawn_key, analysis_configurations):
    """
    Filters a list of message or participant data for objects that opted-in and are fully labelled under all of
    the given coding plans.

    For the definition of "labelled", see `AnalysisUtils.labelled`

    :param data: Message or participant data to filter.
    :type data: TracedData iterable
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param coding_plans: Coding plans specifying the fields in each TracedData object in `data` to look up.
    :type coding_plans: list of src.lib.pipeline_configuration.CodingPlan
    :return: data, filtered for only the objects that opted-in and are labelled under all of the coding plans.
    :rtype: list of TracedData
    """
    fully_labelled = []
    for td in data:
        td_is_labelled = True
        for config in analysis_configurations:
            if not labelled(td, consent_withdrawn_key, config):
                td_is_labelled = False

        if td_is_labelled:
            fully_labelled.append(td)

    return fully_labelled


def filter_relevant(data, consent_withdrawn_key, analysis_configurations):
    """
    Filters a list of message or participant data for objects that are relevant to at least one of the given coding
    plans.

    For the definition of "relevant", see `AnalysisUtils.relevant`

    :param data: Message or participant data to filter.
    :type data: TracedData iterable
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param coding_plans: Coding plans specifying the fields in each TracedData object in `data` to look up.
    :type coding_plans: list of src.lib.pipeline_configuration.CodingPlan
    :return: data, filtered for only the objects that are relevant to at least one of the coding plans.
    :rtype: list of TracedData
    """
    relevant_data = []
    for td in data:
        for config in analysis_configurations:
            if relevant(td, consent_withdrawn_key, config):
                relevant_data.append(td)
                break
    return relevant_data
