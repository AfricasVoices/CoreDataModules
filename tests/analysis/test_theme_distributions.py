from core_data_modules.analysis import theme_distributions
from tests.analysis.AnalysisTestCase import AnalysisTestCase


class TestThemeDistributions(AnalysisTestCase):
    def test_export_theme_distributions_csv(self):
        analysis_data = self.analysis_data
        file_path = f"{self.test_dir}/theme_distributions.csv"

        with open(file_path, "w") as f:
            theme_distributions.export_theme_distributions_csv(
                analysis_data.participants, analysis_data.CONSENT_WITHDRAWN_FIELD,
                analysis_data.rqa_configs, analysis_data.demographic_configs, f
            )

        self.assertFilesEqual(file_path, "tests/analysis/resources/expected/expected_theme_distributions.csv")
