import collections
import time
import unittest
import uuid

import six
from core_data_modules.util import PhoneNumberUuidTable


class TestPhoneNumberUuidTable(unittest.TestCase):
    def test_add_get_phone(self):
        lut = PhoneNumberUuidTable()
        uuid = lut.add_phone("01234123123")
        self.assertEqual(lut.get_uuid("01234123123"), uuid)
        self.assertEqual(lut.add_phone("01234123123"), uuid)
        self.assertRaises(KeyError, lambda: lut.get_uuid("01234000001"))

    def test___getitem__(self):
        lut = PhoneNumberUuidTable()
        uuid = lut.add_phone("01234123123")
        self.assertEqual(lut["01234123123"], uuid)
        self.assertRaises(KeyError, lambda: lut["01234000001"])

    def test_dumps_loads(self):
        lut = PhoneNumberUuidTable()
        lut.add_phone("01234000001")
        lut.add_phone("01234000002")
        lut.add_phone("01234000003")

        dumped = lut.dumps()
        loaded = lut.loads(dumped)

        self.assertEqual(lut, loaded)

    def test_numbers(self):
        lut = PhoneNumberUuidTable()
        lut.add_phone("01234000001")
        lut.add_phone("01234000002")

        if six.PY2:
            self.assertIs(type(lut.numbers()), list)
        if six.PY3:
            self.assertIsInstance(iter(lut.numbers()), collections.Iterable)

        self.assertSetEqual(set(lut.numbers()), {"01234000001", "01234000002"})

    def test_iternumbers(self):
        lut = PhoneNumberUuidTable()
        if six.PY2:
            lut.add_phone("01234000001")
            lut.add_phone("01234000002")
            self.assertSetEqual(set(lut.iternumbers()), {"01234000001", "01234000002"})
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

    @staticmethod
    def time_table_operations():
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
