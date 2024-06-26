from collections import OrderedDict

from core_data_modules.analysis import analysis_utils
from core_data_modules.analysis.analysis_utils import compute_percentage_str
from core_data_modules.cleaners import Codes
from core_data_modules.data_models import CodeTypes


class ThemeAnalysis:
    """
    Represents the analysis done on a single theme.
    """

    def __init__(self, code_scheme_id, code_id, display_text, string_value, theme_type, total_consenting_participants):
        """
        :param code_scheme_id: Id of the code scheme that this theme belongs to.
        :type code_scheme_id: str
        :param code_id: Code id of this theme within the code scheme.
        :type code_id: str
        :param display_text: Text to show users in visualisations.
        :type display_text: str
        :param string_value: Label to use for this theme in CSV exports.
        :type string_value: str
        :param theme_type: One of core_data_modules.data_models.CodeTypes.
        :type theme_type: str
        :param total_consenting_participants: Total number of consenting participants that were labelled with this
                                              theme.
        :type total_consenting_participants: int
        """
        self.code_scheme_id = code_scheme_id
        self.code_id = code_id
        self.display_text = display_text
        self.string_value = string_value
        self.theme_type = theme_type
        self.total_consenting_participants = total_consenting_participants

    def to_dict(self):
        return {
            "code_scheme_id": self.code_scheme_id,
            "code_id": self.code_id,
            "display_text": self.display_text,
            "string_value": self.string_value,
            "theme_type": self.theme_type,
            "total_consenting_participants": self.total_consenting_participants
        }


class DatasetAnalysis:
    """
    Represents the analysis done on a single dataset.
    """

    def __init__(self, dataset_id, total_relevant_participants, theme_distributions):
        """
        :param dataset_id: Id to give this dataset.
        :type dataset_id: str
        :param total_relevant_participants: The total number of consenting participants who gave a relevant response
                                            to this dataset.
        :type total_relevant_participants: int
        :param theme_distributions: Per-theme analysis for this dataset.
        :type theme_distributions: list of ThemeAnalysis
        """
        self.dataset_id = dataset_id
        self.total_relevant_participants = total_relevant_participants
        self.theme_distributions = theme_distributions

    def to_dict(self):
        return {
            "dataset_id": self.dataset_id,
            "total_relevant_participants": self.total_relevant_participants,
            "theme_distributions": [dist.to_dict() for dist in self.theme_distributions]
        }


class ThemeDistributionsAnalysis:
    """
    Represents the results of a theme distributions analysis.
    """

    def __init__(self, dataset_analyses):
        """
        :param: Dataset analyses conducted in this theme distributions analysis.
        :type dataset_analyses: list of DatasetAnalysis
        """
        self.datasets = dataset_analyses

    def to_dict(self):
        return {
            "datasets": [dataset.to_dict() for dataset in self.datasets]
        }


def _non_stop_codes(codes):
    """
    Filters a list of codes for those that do not have control code Codes.STOP.

    :param codes: Codes to filter.
    :type codes: list of core_data_modules.data_models.Code
    :return: All codes in `codes` except those with control code Codes.STOP.
    :rtype: list of core_data_modules.data_models.Code
    """
    return [code for code in codes if code.control_code != Codes.STOP]


def _compute_dataset_theme_distributions(participants, consent_withdrawn_field, dataset_configuration,
                                         breakdown_configurations):
    """
    Computes the theme distributions for a list of participants, for a single dataset.

    :param participants: Participants to compute the theme_distributions for.
    :type participants: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param dataset_configuration: Configuration for the themes. It should contain:
                                  - dataset_name. This will be used to index the returned theme_distributions dict
                                    (the "theme dataset_name" above).
                                  - code_scheme. This will be used to index each themes dictionary in the returned
                                    theme_distributions dict (the "theme" above). Themes are formatted as
                                    {theme_configuration.dataset_name}_{code.string_value} for each code in the
                                    code_scheme.
    :type dataset_configuration: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param breakdown_configurations: Configuration for the breakdowns dict.
                                     For details, see `theme_distributions._make_breakdowns_dict`.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Theme distributions results for one dataset.
    :rtype: DatasetAnalysis
    """
    # Initialise theme totals for each theme in the dataset
    theme_analyses = OrderedDict()
    for code in _non_stop_codes(dataset_configuration.code_scheme.codes):
        theme_analyses[code.code_id] = ThemeAnalysis(
            code_scheme_id=dataset_configuration.code_scheme.scheme_id,
            code_id=code.code_id,
            display_text=code.display_text,
            string_value=code.string_value,
            theme_type=code.code_type,
            total_consenting_participants=0
        )

    episode_total_relevant_participants = 0

    # Calculate all the theme_distributions data for this dataset
    for participant in participants:
        # Total relevance for this episode
        if analysis_utils.relevant(participant, consent_withdrawn_field, dataset_configuration):
            episode_total_relevant_participants += 1

        # Totals for each theme
        for code in _non_stop_codes(analysis_utils.get_codes_from_td(participant, dataset_configuration)):
            theme_analyses[code.code_id].total_consenting_participants += 1

    return DatasetAnalysis(
        dataset_id=dataset_configuration.dataset_name,
        total_relevant_participants=episode_total_relevant_participants,
        theme_distributions=list(theme_analyses.values())
    )


def compute_theme_distributions(participants, consent_withdrawn_field, dataset_configurations, breakdown_configurations):
    """
    Computes the theme distributions for a list of participants.

    :param participants: Participants to compute the theme_distributions for.
    :type participants: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param dataset_configurations: Configuration for the themes. Each configuration should contain:
                                  - dataset_name. This will be used to index the returned theme_distributions dict
                                    (the "theme dataset_name" above).
                                  - code_scheme. This will be used to index each themes dictionary in the returned
                                    theme_distributions dict (the "theme" above). Themes are formatted as
                                    {theme_configuration.dataset_name}_{code.string_value} for each code in the
                                    code_scheme.
    :type dataset_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param breakdown_configurations: Configuration for the breakdowns dict.
                                     For details, see `theme_distributions._make_breakdowns_dict`.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :return: Theme distributions results
    :rtype: ThemeDistributionsAnalysis
    """
    participants = analysis_utils.filter_opt_ins(participants, consent_withdrawn_field)

    dataset_analyses = []
    for dataset_config in dataset_configurations:
        dataset_analyses.append(
            _compute_dataset_theme_distributions(
                participants, consent_withdrawn_field, dataset_config, breakdown_configurations
            )
        )

    return ThemeDistributionsAnalysis(
        dataset_analyses=dataset_analyses
    )


def export_theme_distributions_csv(participants, consent_withdrawn_field, dataset_configurations,
                                   breakdown_configurations, f):
    """
    Computes the theme_distributions and exports them to a CSV.

    The CSV will contain the headers:
     - Dataset, set to the dataset_name in each of the `theme_configurations`, de-duplicated for clarity).
     - Theme, set to {dataset_name}_{code.string_value}, for each code in each theme_configuration.
     - Total Participants
     - Total Participants %
    and raw total and % headers for each scheme and code in the `breakdown_configurations`.

    TODO: Implement breakdowns

    :param participants: Participants to compute the theme_distributions for.
    :type participants: iterable of core_data_modules.traced_data.TracedData
    :param consent_withdrawn_field: Field in each individuals object which records if consent is withdrawn.
    :type consent_withdrawn_field: str
    :param dataset_configurations: Configuration for the themes. Each configuration should contain:
                                  - dataset_name. This will be used to index the returned theme_distributions dict
                                    (the "theme dataset_name" above).
                                  - code_scheme. This will be used to index each themes dictionary in the returned
                                    theme_distributions dict (the "theme" above). Themes are formatted as
                                    {theme_configuration.dataset_name}_{code.string_value} for each code in the
                                    code_scheme.
    :type dataset_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param breakdown_configurations: Configuration for the breakdowns dict.
                                     For details, see `theme_distributions._make_breakdowns_dict`.
    :type breakdown_configurations: iterable of core_data_modules.analysis.AnalysisConfiguration
    :param f: File to write the theme_distributions CSV to.
    :type f: file-like
    """
    theme_distributions = compute_theme_distributions(participants, consent_withdrawn_field, dataset_configurations,
                                                      breakdown_configurations)

    rows = []
    for dataset in theme_distributions.datasets:
        rows.append({
            "Dataset": dataset.dataset_id,
            "Theme": "Total Relevant Participants",
            "Total Participants": dataset.total_relevant_participants,
            "Total Participants %": compute_percentage_str(1, 1)  # 100%, via compute_percentage_str for the formatting
        })

        for theme in dataset.theme_distributions:
            rows.append({
                "Dataset": "",
                "Theme": theme.string_value,
                "Total Participants": theme.total_consenting_participants,
                "Total Participants %": compute_percentage_str(
                    theme.total_consenting_participants, dataset.total_relevant_participants
                ) if theme.theme_type == CodeTypes.NORMAL else ""
            })

    headers = ["Dataset", "Theme", "Total Participants", "Total Participants %"]

    analysis_utils.write_csv(
        rows,
        headers,
        f
    )
