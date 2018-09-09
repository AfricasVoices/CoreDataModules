import filecmp
import shutil
import tempfile
import unittest
from os import path

from core_data_modules.cleaners.code_scheme import CodeScheme


class TestCodeScheme(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_export_to_coda_scheme_file(self):
        file_path = path.join(self.test_dir, "coda_scheme_export_test.csv")

        code_scheme = CodeScheme(scheme_id=2, name="YesNo", code_names=["yes", "no"], add_codes_for_missing=True)
        with open(file_path, "w") as f:
            code_scheme.export_to_coda_scheme_file(f)
        self.assertTrue(filecmp.cmp(file_path, "tests/cleaners/resources/coda_export_expected_code_scheme.csv"))
