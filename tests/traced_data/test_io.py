import filecmp
import random
import shutil
import tempfile
import time
import unittest
from os import path

from core_data_modules import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataCodaIO, TracedDataJsonIO


def generate_traced_data_frame():
    random.seed(0)
    for i, text in enumerate(["female", "m", "WoMaN", "27", "female"]):
        d = {"URN": "+001234500000" + str(i), "Gender": text}
        yield TracedData(d, Metadata("test_user", "data_generator", i))


class TestTracedDataCodaIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_traced_data_iterable_to_coda(self):
        file_path = path.join("coda_test.csv")

        # Test exporting everything
        data = generate_traced_data_frame()
        with open(file_path, "wb") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda(data, "Gender", f)
        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output_coded.csv"))

        # Test exporting only not coded elements
        data = list(generate_traced_data_frame())
        data[0].append_data({"Gender_clean": None}, Metadata("test_user", "cleaner", 10))
        data[2].append_data({"Gender_clean": "F"}, Metadata("test_user", "cleaner", 11))
        data[4].append_data({"Gender_clean": "F"}, Metadata("test_user", "cleaner", 12))
        with open(file_path, "wb") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda(
                data, "Gender", f, exclude_coded_with_key="Gender_clean")
        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output_not_coded.csv"))

    def test_import_coda_to_traced_data_iterable(self):
        self._overwrite_false_asserts()
        self._overwrite_true_asserts()

    def _overwrite_false_asserts(self):
        data = list(generate_traced_data_frame())
        data[0].append_data({"Gender_clean": "X"}, Metadata("test_user", "cleaner", 20))

        file_path = "tests/traced_data/resources/coda_import_data.txt"
        with open(file_path, "rb") as f:
            data = list(TracedDataCodaIO.import_coda_to_traced_data_iterable(
                "test_user", data, "Gender", "Gender_clean", f))

        expected_data = [
            {"URN": "+0012345000000", "Gender": "female", "Gender_clean": "X"},
            {"URN": "+0012345000001", "Gender": "m", "Gender_clean": "M"},
            {"URN": "+0012345000002", "Gender": "WoMaN", "Gender_clean": "F"},
            {"URN": "+0012345000003", "Gender": "27", "Gender_clean": None},
            {"URN": "+0012345000004", "Gender": "female", "Gender_clean": "F"}
        ]

        self.assertEqual(len(data), len(expected_data))

        for x, y in zip(data, expected_data):
            self.assertDictEqual(dict(x.items()), y)

    def _overwrite_true_asserts(self):
        data = list(generate_traced_data_frame())
        data[0].append_data({"Gender_clean": "X"}, Metadata("test_user", "cleaner", 20))

        file_path = "tests/traced_data/resources/coda_import_data.txt"
        with open(file_path, "rb") as f:
            data = list(TracedDataCodaIO.import_coda_to_traced_data_iterable(
                "test_user", data, "Gender", "Gender_clean", f, True))

        expected_data = [
            {"URN": "+0012345000000", "Gender": "female", "Gender_clean": "F"},
            {"URN": "+0012345000001", "Gender": "m", "Gender_clean": "M"},
            {"URN": "+0012345000002", "Gender": "WoMaN", "Gender_clean": "F"},
            {"URN": "+0012345000003", "Gender": "27", "Gender_clean": None},
            {"URN": "+0012345000004", "Gender": "female", "Gender_clean": "F"}
        ]

        self.assertEqual(len(data), len(expected_data))

        for x, y in zip(data, expected_data):
            self.assertDictEqual(dict(x.items()), y)


class TestTracedDataJsonIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_export_traced_data_iterable_to_json(self):
        file_path = path.join(self.test_dir, "json_test.json")
        data = generate_traced_data_frame()

        with open(file_path, "wb") as f:
            TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/json_export_expected.json"))

    def test_import_json_to_traced_data_iterable(self):
        file_path = "tests/traced_data/resources/json_export_expected.json"
        expected = list(generate_traced_data_frame())

        with open(file_path, "rb") as f:
            imported = list(TracedDataJsonIO.import_json_to_traced_data_iterable(f))

        self.assertListEqual(expected, imported)
