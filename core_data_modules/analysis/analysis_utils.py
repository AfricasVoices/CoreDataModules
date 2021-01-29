import csv

from core_data_modules.cleaners import Codes
from core_data_modules.data_models.code_scheme import CodeTypes


class AnalysisConfiguration(object):
    def __init__(self, dataset_name, raw_field, coded_field, code_scheme):
        self.dataset_name = dataset_name
        self.raw_field = raw_field
        self.coded_field = coded_field
        self.code_scheme = code_scheme


def get_codes_from_td(td, analysis_configuration):
    """
    Returns all the codes from a traced data object under the coded_field and code_scheme in the given
    analysis_configuration.

    :param td: TracedData to get the codes from.
    :type td: core_data_modules.traced_data.TracedData
    :param analysis_configuration: Analysis configuration to use to get the codes.
                                   The coded_field sets field to look-up in each TracedData.
                                   The code_scheme is used to convert the labels to their corresponding codes.
    :type analysis_configuration: AnalysisConfiguration
    :return: Codes for the labels in this TracedData's `analysis_configuration.coded_field`.
    :rtype: list of core_data_modules.data_models.Code
    """
    coded_field = analysis_configuration.coded_field

    if coded_field not in td:
        return []

    # TracedData can contain a single label or a list of labels. Read into a list of labels in all cases.
    if type(td[coded_field]) == list:
        labels = td[coded_field]
    else:
        labels = [td[coded_field]]

    # Convert the labels to their corresponding code objects
    codes = [analysis_configuration.code_scheme.get_code_with_code_id(label["CodeID"]) for label in labels]

    return codes


def responded(td, analysis_configuration):
    """
    Returns whether the given TracedData object contains a response under the given analysis_configuration.

    The TracedData is considered to contain a response if its analysis_configuration.coded_field has been labelled
    with anything other than codes with control code Codes.TRUE_MISSING or Codes.SKIPPED.

    :param td: TracedData to check.
    :type td: core_data_modules.traced_data.TracedData
    :param analysis_configuration: Analysis configuration to use to check if the TracedData contains a response.
                                   This determines the coded_field to check and the code_scheme to use to interpret it.
    :type analysis_configuration: AnalysisConfiguration
    :return: Whether `td` contains a response under the `analysis_configuration`.
    :rtype: bool
    """
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
    Returns whether the given TracedData object contains an opt-in response under the given analysis_configuration.

    The TracedData is considered to contain an opt-in if its analysis_configuration.coded_field contains a response
    and the TracedData is not an opt-out.

    For more details, see `analysis_utils.responded` and `analysis_utils.withdrew_consent`.

    :param td: TracedData to check.
    :type td: core_data_modules.traced_data.TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param analysis_configuration: Analysis configuration to use to check if the TracedData contains an opt-in.
                                   This determines the coded_field to check and the code_scheme to use to interpret it.
    :type analysis_configuration: AnalysisConfiguration
    :return: Whether `td` contains a response under the `analysis_configuration` and did not withdraw consent.
    :rtype: bool
    """
    if withdrew_consent(td, consent_withdrawn_key):
        return False

    return responded(td, analysis_configuration)


def labelled(td, consent_withdrawn_key, analysis_configuration):
    """
    Returns whether the given TracedData object has been labelled under the given analysis_configuration.

    An object is considered labelled if all of the following hold:
     - Consent was not withdrawn.
     - A response was received (see `AnalysisUtils.responded` for the definition of this).
     - The response has been assigned at least one label.
     - None of the assigned labels have the control_code Codes.NOT_REVIEWED.

    :param td: TracedData to check.
    :type td: TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param analysis_configuration: Analysis configuration to use to check if the TracedData has been labelled.
                                   This determines the coded_field to check and the code_scheme to use to interpret it.
    :type analysis_configuration: AnalysisConfiguration
    :return: Whether `td` contains a labelled response to `coding_plan` and did not withdraw consent.
    :rtype: bool
    """
    if withdrew_consent(td, consent_withdrawn_key):
        return False

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

    A response is considered relevant if it is labelled with a normal code.

    For the definition of labelled, see `analysis_utils.labelled`.

    :param td: TracedData to check.
    :type td: TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param analysis_configuration: Analysis configuration to use to check if the TracedData is relevant.
                                   This determines the coded_field to check and the code_scheme to use to interpret it.
    :type analysis_configuration: AnalysisConfiguration
    :return: Whether `td` contains a relevant response to `coding_plan`.
    :rtype: bool
    """
    if not labelled(td, consent_withdrawn_key, analysis_configuration):
        return False

    codes = get_codes_from_td(td, analysis_configuration)
    for code in codes:
        if code.code_type == CodeTypes.NORMAL:
            return True

    return False


def filter_opt_ins(data, consent_withdrawn_key, analysis_configurations):
    """
    Filters a list of message or participant data for objects that opted-in and contained a response under at least
    one of the given analysis_configurations.

    For the definition of "opt-in", see `AnalysisUtils.opt_in`.

    :param data: Message or participant data to filter.
    :type data: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param analysis_configurations: Analysis configurations to use to check if each TracedData contains an opt-in.
    :type analysis_configurations: iterable of AnalysisConfiguration
    :return: data, filtered for only the objects that opted-in and responded to at least one of the analysis_configurations.
    :rtype: list of core_data_modules.traced_data.TracedData
    """
    opt_ins = []
    for td in data:
        for config in analysis_configurations:
            if opt_in(td, consent_withdrawn_key, config):
                opt_ins.append(td)
                break
    return opt_ins


def filter_partially_labelled(data, consent_withdrawn_key, analysis_configurations):
    """
    Filters a list of message or participant data for objects that opted-in and are labelled under at least
    one of the given analysis_configurations.

    For the definition of "labelled", see `AnalysisUtils.labelled`

    :param data: Message or participant data to filter.
    :type data: TracedData iterable
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param analysis_configurations: Analysis configurations to use to check if each TracedData has been partially
                                    labelled.
    :type analysis_configurations: iterable of AnalysisConfiguration
    :return: `data`, filtered for only the objects that opted-in and are labelled under at least one of the coding
             plans.
    :rtype: list of TracedData
    """
    partially_labelled = []
    for td in data:
        for plan in analysis_configurations:
            if labelled(td, consent_withdrawn_key, plan):
                partially_labelled.append(td)
                break
    return partially_labelled


def filter_fully_labelled(data, consent_withdrawn_key, analysis_configurations):
    """
    Filters a list of message or participant data for objects that opted-in and are labelled under all of
    the given analysis_configurations.

    For the definition of "labelled", see `AnalysisUtils.labelled`

    :param data: Message or participant data to filter.
    :type data: TracedData iterable
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param analysis_configurations: Analysis configurations to use to check if each TracedData has been fully
                                    labelled.
    :type analysis_configurations: iterable of AnalysisConfiguration
    :return: data, filtered for the objects that are labelled under all of the analysis_configurations.
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
    Filters a list of message or participant data for objects that are relevant to at least one of the given
    analysis_configurations.

    For the definition of "relevant", see `AnalysisUtils.relevant`

    :param data: Message or participant data to filter.
    :type data: TracedData iterable
    :param consent_withdrawn_key: Key in the TracedData of the consent withdrawn field.
    :type consent_withdrawn_key: str
    :param analysis_configurations: Analysis configurations to use to check if each TracedData is relevant.
    :type analysis_configurations: iterable of AnalysisConfiguration
    :return: data, filtered for the objects that are relevant to at least one of the analysis_configurations.
    :rtype: list of TracedData
    """
    relevant_data = []
    for td in data:
        for config in analysis_configurations:
            if relevant(td, consent_withdrawn_key, config):
                relevant_data.append(td)
                break
    return relevant_data


def compute_percentage_str(x, y):
    """
    Formats x as a percentage of y as a string to 1 decimal place.

    If y is 0, returns "-".

    :param x: Dividend.
    :type x: number
    :param y: Divisor.
    :type y: number
    :return: "-" if y == 0, otherwise x / y to 1 decimal place.
    :rtype: str
    """
    if y == 0:
        return "-"
    else:
        return str(round(x / y * 100, 1))


def write_csv(data, headers, f):
    """
    Writes data to a CSV.

    :param data: Data to write, as rows.
    :type data: iterable of dict
    :param headers: CSV headers.
    :type headers: list of str
    :param f: File to write the CSV to.
    :type f: file-like
    """
    writer = csv.DictWriter(f, fieldnames=headers, lineterminator="\n")
    writer.writeheader()

    for row in data:
        writer.writerow(row)
