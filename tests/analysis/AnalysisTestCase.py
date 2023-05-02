import filecmp
import shutil
import tempfile
import unittest

from tests.analysis.generate_analysis_test_dataset import generate_synthetic_analysis_data


class AnalysisTestCase(unittest.TestCase):
    analysis_data = generate_synthetic_analysis_data()

    def setUp(self):
        """
        Assigns a temporary working directory to `self.test_dir`, which subclasses can use to write temporary test data
        to.

        See also: `unittest.TestCase.setUp`, which this method implements.
        """
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        Deletes the temporary working directory.

        See also: `unittest.TestCase.tearDown`, which this method implements.
        """
        shutil.rmtree(self.test_dir)

    def assertFilesEqual(self, file_path_a, file_path_b):
        """
        Asserts the files at the two referenced paths have contents that match exactly.

        :param file_path_a: Path to the first file to compare.
        :type file_path_a: str
        :param file_path_b: Path to the other file to compare.
        :type file_path_b: str
        """
        self.assertTrue(filecmp.cmp(file_path_a, file_path_b))


