from collections import OrderedDict

from core_data_modules.analysis import analysis_utils
from core_data_modules.analysis.analysis_utils import compute_percentage_str
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

    def __init__(self, datasets):
        """
        :type datasets: dict of str -> list of DatasetAnalysis
        """
        self.datasets = datasets

    def to_dict(self):
        return {
            "datasets": [ep.to_dict() for ep in self.datasets]
        }


def _compute_dataset_theme_distributions(participants, consent_withdrawn_field, dataset_configuration,
                                         breakdown_configurations):
    """
    :type episode_configuration: core_data_modules.analysis.AnalysisConfiguration
    """
    # Initialise theme totals for each theme in the dataset
    theme_analyses = OrderedDict()
    for code in dataset_configuration.code_scheme.codes:
        theme_analyses[code.code_id] = ThemeAnalysis(
            code_scheme_id=dataset_configuration.code_scheme.scheme_id,
            code_id=code.code_id,
            display_text=code.display_text,
            string_value=code.string_value,
            theme_type=code.code_type,
            total_consenting_participants=0
        )

    episode_total_relevant_participants = 0

    # Iterate over the participants, incrementing total relevant and
    for participant in participants:
        if analysis_utils.relevant(participant, consent_withdrawn_field, dataset_configuration):
            episode_total_relevant_participants += 1

        for code in analysis_utils.get_codes_from_td(participant, dataset_configuration):
            theme_analyses[code.code_id].total_consenting_participants += 1

    return DatasetAnalysis(
        dataset_id=dataset_configuration.dataset_name,
        total_relevant_participants=episode_total_relevant_participants,
        theme_distributions=list(theme_analyses.values())
    )


def compute_theme_distributions(participants, consent_withdrawn_field, theme_configurations, breakdown_configurations):
    participants = analysis_utils.filter_opt_ins(participants, consent_withdrawn_field)

    episode_analyses = []
    for episode_config in theme_configurations:
        episode_analyses.append(
            _compute_dataset_theme_distributions(
                participants, consent_withdrawn_field, episode_config, breakdown_configurations
            )
        )

    return ThemeDistributionsAnalysis(
        datasets=episode_analyses
    )


def export_theme_distributions_csv(participants, consent_withdrawn_field, theme_configurations,
                                   breakdown_configurations, f):
    theme_distributions = compute_theme_distributions(participants, consent_withdrawn_field, theme_configurations,
                                                      breakdown_configurations)

    rows = []
    for dataset in theme_distributions.datasets:
        rows.append({
            "Dataset": dataset.dataset_id,
            "Theme": "Total Relevant Participants",
            "Total Participants": dataset.total_relevant_participants,
            "Total Participants %": "100"
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
