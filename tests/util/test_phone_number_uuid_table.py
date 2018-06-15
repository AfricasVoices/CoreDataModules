import collections
import filecmp
import shutil
import tempfile
import time
import unittest
import uuid
from os import path

import six
from core_data_modules.util import PhoneNumberUuidTable


class TestPhoneNumberUuidTable(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_get_phone(self):
        lut = PhoneNumberUuidTable()
        uuid = lut.add_phone("01234123123")
        self.assertEqual(lut.get_uuid("01234123123"), uuid)
        self.assertEqual(lut.get_uuid("(01234) 123123"), uuid)
        self.assertEqual(lut.add_phone("01234123123"), uuid)
        self.assertEqual(lut.add_phone("+1234 123-123"), uuid)
        self.assertRaises(KeyError, lambda: lut.get_uuid("01234000001"))

    def test_numbers(self):
        lut = PhoneNumberUuidTable()
        lut.add_phone("1234000001")
        lut.add_phone("1234000002")

        if six.PY2:
            self.assertIs(type(lut.numbers()), list)
        if six.PY3:
            self.assertIsInstance(iter(lut.numbers()), collections.Iterable)

        self.assertSetEqual(set(lut.numbers()), {"1234000001", "1234000002"})

    def test_iternumbers(self):
        lut = PhoneNumberUuidTable()
        if six.PY2:
            lut.add_phone("1234000001")
            lut.add_phone("1234000002")
            self.assertSetEqual(set(lut.iternumbers()), {"1234000001", "1234000002"})
        if six.PY3:
            self.assertRaises(AttributeError, lambda: lut.iternumbers())

    def test_uuids(self):
        lut = PhoneNumberUuidTable()
        uuids = {lut.add_phone("01234000001"), lut.add_phone("01234000002")}

        if six.PY2:
            self.assertIs(type(lut.uuids()), list)
        if six.PY3:
            self.assertIsInstance(iter(lut.uuids()), collections.Iterable)

        self.assertSetEqual(set(lut.uuids()), uuids)

    def test_iteruuids(self):
        lut = PhoneNumberUuidTable()
        if six.PY2:
            uuids = {lut.add_phone("01234000001"), lut.add_phone("01234000002")}
            self.assertSetEqual(set(lut.iteruuids()), uuids)
        if six.PY3:
            self.assertRaises(AttributeError, lambda: lut.iteruuids())

    def test_dumps_loads(self):
        lut = PhoneNumberUuidTable()
        lut.add_phone("01234000001")
        lut.add_phone("01234000002")
        lut.add_phone("01234000003")

        dumped = lut.dumps()
        loaded = lut.loads(dumped)

        self.assertEqual(lut, loaded)
        
    def get_dump_load_lut(self):
        table = {
            "1234000001": "4bf3388a-039b-4ca7-8789-319cf8ee343c",
            "1234000002": "62815f71-2721-42a6-856c-9cd66b66d6b5",
            "1234000003": "6becf322-7819-44f1-b212-5a13066def17"
        }

        lut = PhoneNumberUuidTable(table)
        self.assertEqual(lut.get_uuid("01234000003"), "6becf322-7819-44f1-b212-5a13066def17")
        self.assertEqual(lut.get_phone("62815f71-2721-42a6-856c-9cd66b66d6b5"), "1234000002")
        
        return lut

    def test_dump(self):
        file_path = path.join(self.test_dir, "test_output.json")
        lut = self.get_dump_load_lut()

        with open(file_path, "w") as f:
            lut.dump(f, sort_keys=True)

        self.assertTrue(filecmp.cmp(file_path, "tests/util/resources/phone_number_table_sample.json"))

    def test_load(self):
        with open("tests/util/resources/phone_number_table_sample.json", "r") as f:
            lut = PhoneNumberUuidTable.load(f)

        expected = self.get_dump_load_lut()
        self.assertEqual(lut, expected)

    @staticmethod
    def time_table_operations():
        """
        Times various PhoneNumberUuidTable options with 100k numbers.

        Not automatically run as part of the test suite.
        """
        lut = PhoneNumberUuidTable()

        print("Times:")

        # Generate 100k UUIDs
        start = time.time()
        for x in range(100000):
            str(uuid.uuid4())
        end = time.time()
        print("Generate 100k UUIDs", end - start)

        # Generate some phone numbers
        numbers = []
        for x in range(100000):
            numbers.append("+44123456" + str(x).zfill(6))

        # Add all of those phone numbers to the LUT.
        start = time.time()
        uuids = []
        for n in numbers:
            uuids.append(lut.add_phone(n))
        end = time.time()
        print("Add 100k numbers", end - start)

        # Read all of the numbers in the LUT.
        start = time.time()
        for u in uuids:
            lut.get_phone(u)
        end = time.time()
        print("Lookup 100k numbers", end - start)

        # Serialize
        start = time.time()
        dumped = lut.dumps()
        end = time.time()
        print("Serialize to json string", end - start)

        # Deserialize
        start = time.time()
        PhoneNumberUuidTable.loads(dumped)
        end = time.time()
        print("Deserialize from json string", end - start)
