from collections import OrderedDict

from core_data_modules.analysis import analysis_utils


class ThemeAnalysis:
    def __init__(self, scheme_id, code_id, display_text, string_value, theme_type, total_consenting_participants):
        """
        :type display_text: str
        :type theme_type: str
        :type total_consenting_participants: int
        """
        self.scheme_id = scheme_id
        self.code_id = code_id
        self.display_text = display_text
        self.string_value = string_value
        self.theme_type = theme_type
        self.total_consenting_participants = total_consenting_participants

    def to_dict(self):
        return {
            "scheme_id": self.scheme_id,
            "code_id": self.code_id,
            "display_text": self.display_text,
            "string_value": self.string_value,
            "theme_type": self.theme_type,
            "total_consenting_participants": self.total_consenting_participants
        }


class EpisodeAnalysis:
    def __init__(self, episode_id, total_relevant_participants, theme_distributions):
        """
        :type episode_id: str
        :type total_relevant_participants: int
        :type theme_distributions: list of ThemeAnalysis
        """
        self.episode_id = episode_id
        self.total_relevant_participants = total_relevant_participants
        self.theme_distributions = theme_distributions

    def to_dict(self):
        return {
            "episode_id": self.episode_id,
            "total_relevant_participants": self.total_relevant_participants,
            "theme_distributions": [dist.to_dict() for dist in self.theme_distributions]
        }


class ThemeDistributions:
    def __init__(self, episodes):
        """
        :type episodes: dict of str -> list of EpisodeAnalysis
        """
        self.episodes = episodes

    def to_dict(self):
        return {
            "episodes": [ep.to_dict() for ep in self.episodes]
        }


def _compute_episode_theme_distributions(participants, consent_withdrawn_field, episode_configuration,
                                         breakdown_configurations):
    """
    :type episode_configuration: core_data_modules.analysis.AnalysisConfiguration
    """
    # Initialise theme totals for each theme in the dataset
    theme_analyses = OrderedDict()
    for code in episode_configuration.code_scheme.codes:
        theme_analyses[code.code_id] = ThemeAnalysis(
            scheme_id=episode_configuration.code_scheme.scheme_id,
            code_id=code.code_id,
            display_text=code.display_text,
            string_value=code.string_value,
            theme_type=code.code_type,
            total_consenting_participants=0
        )

    episode_total_relevant_participants = 0

    # Iterate over the participants, incrementing total relevant and
    for participant in participants:
        if analysis_utils.relevant(participant, consent_withdrawn_field, episode_configuration):
            episode_total_relevant_participants += 1

        for code in analysis_utils.get_codes_from_td(participant, episode_configuration):
            theme_analyses[code.code_id].total_consenting_participants += 1

    return EpisodeAnalysis(
        episode_id=episode_configuration.dataset_name,
        total_relevant_participants=episode_total_relevant_participants,
        theme_distributions=list(theme_analyses.values())
    )


def compute_theme_distributions(participants, consent_withdrawn_field, theme_configurations, breakdown_configurations):
    participants = analysis_utils.filter_opt_ins(participants, consent_withdrawn_field)

    episode_analyses = []
    for episode_config in theme_configurations:
        episode_analyses.append(
            _compute_episode_theme_distributions(
                participants, consent_withdrawn_field, episode_config, breakdown_configurations
            )
        )

    return ThemeDistributions(
        episodes=episode_analyses
    )


def export_theme_distributions_csv(participants, consent_withdrawn_field, theme_configurations,
                                   breakdown_configurations, f):
    theme_distributions = compute_theme_distributions(participants, consent_withdrawn_field, theme_configurations,
                                                      breakdown_configurations)

    rows = []
    last_dataset_name = None
    for ep in theme_distributions.episodes:
        for theme in ep.theme_distributions:
            dataset_name = ep.episode_id
            row = {
                "Dataset": dataset_name if dataset_name != last_dataset_name else "",
                "Theme": theme.string_value,
                "Total Participants": ep.total_relevant_participants,
                "Total Participants %": "100"
            }
            rows.append(row)

    headers = ["Dataset", "Theme", "Total Participants", "Total Participants %"]

    analysis_utils.write_csv(
        rows,
        headers,
        f
    )
