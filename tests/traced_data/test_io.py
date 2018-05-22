import filecmp
import random
import shutil
import tempfile
import time
import unittest
from os import path

from core_data_modules import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataCodaIO


def generate_traced_data_frame():
    random.seed(0)
    for i, text in enumerate(["female", "m", "WoMaN", "27"]):
        d = {"URN": "+001234500000" + str(i), "Gender": text}
        yield TracedData(d, Metadata("test_user", "data_generator", time.time()))


class TestTracedDataCodaIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_dump(self):
        data = generate_traced_data_frame()
        file_path = path.join(self.test_dir, "coda_test.csv")

        with open(file_path, "wb") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda(data, "Gender", "URN", f)

        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output.csv"))

    def test_load(self):
        data = generate_traced_data_frame()

        file_path = "tests/traced_data/resources/coda_import_data.txt"
        with open(file_path, "rb") as f:
            data = list(TracedDataCodaIO.import_coda_to_traced_data_iterable(data, "Gender", "CodaCodedGender", f))

        expected_data = [
            {"URN": "+0012345000000", "Gender": "female", "CodaCodedGender": "f"},
            {"URN": "+0012345000001", "Gender": "m", "CodaCodedGender": "m"},
            {"URN": "+0012345000002", "Gender": "WoMaN", "CodaCodedGender": "f"},
            {"URN": "+0012345000003", "Gender": "27", "CodaCodedGender": "NC"}
        ]

        for x, y in zip(data, expected_data):
            self.assertDictEqual(dict(x.items()), y)
