from __future__ import print_function
import random
import shutil
import tempfile
import time
import unittest
from os import path

from core_data_modules.traced_data.excel_io import TracedDataCSVIO
from core_data_modules.traced_data import TracedData, Metadata


def generate_traced_data_frame():
    random.seed(0)
    for i, text in enumerate(["female", "m", "WoMaN", "27"]):
        d = {"URN": "+001234500000" + str(i), "Gender": text}
        yield TracedData(d, Metadata("test_user", "data_generator", time.time()))


class TestTracedDataCSVIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_dump_load(self):
        data = generate_traced_data_frame()
        file_path = path.join(self.test_dir, "excel_test.csv")

        with open(file_path, "wb") as f:
            TracedDataCSVIO.dump(data, f)

        with open(file_path, "rb") as f:
            imported = TracedDataCSVIO.load(f)

            for x, y in zip(generate_traced_data_frame(), imported):
                # TODO: Decide if order matters, then delete one of these tests accordingly.
                self.assertSetEqual(set(x.items()), set(y.items()))
                self.assertListEqual(list(x.items()), list(y.items()))
