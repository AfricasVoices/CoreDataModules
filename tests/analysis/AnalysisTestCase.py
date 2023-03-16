import filecmp
import shutil
import tempfile
import unittest

from tests.analysis.generate_analysis_test_dataset import generate_synthetic_analysis_data


class AnalysisTestCase(unittest.TestCase):
    analysis_data = generate_synthetic_analysis_data()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def assertFilesEqual(self, a, b):
        self.assertTrue(filecmp.cmp(a, b))


