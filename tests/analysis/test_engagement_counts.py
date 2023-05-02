from core_data_modules.analysis.engagement_counts import export_engagement_counts_csv
from tests.analysis.AnalysisTestCase import AnalysisTestCase


class TestEngagementCounts(AnalysisTestCase):
    def test_export_engagement_counts(self):
        analysis_data = self.analysis_data
        file_path = f"{self.test_dir}/engagement_counts.csv"

        with open(file_path, "w") as f:
            export_engagement_counts_csv(
                analysis_data.messages, analysis_data.participants, analysis_data.CONSENT_WITHDRAWN_FIELD,
                analysis_data.rqa_configs, f
            )

        self.assertFilesEqual(file_path, "tests/analysis/resources/expected/expected_engagement_counts.csv")
