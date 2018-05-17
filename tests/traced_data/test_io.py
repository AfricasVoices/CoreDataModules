import filecmp
import random
import shutil
import tempfile
import time
import unittest
from os import path

from core_data_modules import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataCodaIO


class TestTracedDataCodaIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @staticmethod
    def generate_traced_data_frame():
        random.seed(0)
        for i, text in enumerate(["female", "m", "WoMaN", "27"]):
            d = {"Gender": text, "URN": "+001234500000" + str(i)}
            yield TracedData(d, Metadata("test_user", "data_generator", time.time()))

    def test_dump(self):
        data = self.generate_traced_data_frame()
        file_path = path.join("coda_test.csv")

        with open(file_path, "wb") as f:
            TracedDataCodaIO.dump(data, "Gender", f)

        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output.csv"))
