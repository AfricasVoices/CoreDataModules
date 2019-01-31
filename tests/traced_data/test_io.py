# coding=utf-8
import filecmp
import shutil
import tempfile
import time
import unittest
from os import path

from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataCSVIO, TracedDataJsonIO, \
    TracedDataTheInterfaceIO, _td_type_error_string


def generate_traced_data_iterable():
    for i, text in enumerate(["female", "m", "WoMaN", "27", "female"]):
        d = {"URN": "+001234500000" + str(i), "Gender": text}
        yield TracedData(d, Metadata("test_user", "data_generator", i))


def generate_appended_traced_data():
    message_data = {"phone": "+441632000001", "message": "Hello AVF!"}
    message_td = TracedData(message_data, Metadata("test_user", "run_fetcher", 0))
    message_td.append_data({"message": "hello avf"}, Metadata("test_user", "message_cleaner", 1))

    demog_1_data = {"phone": "+441632000001", "gender": "woman", "age": "twenty"}
    demog_1_td = TracedData(demog_1_data, Metadata("test_user", "run_fetcher", 2))
    demog_1_td.append_data({"gender": "female", "age": 20}, Metadata("test_user", "demog_cleaner", 3))

    demog_2_data = {"phone": "+441632000001", "country": "Kenyan citizen"}
    demog_2_td = TracedData(demog_2_data, Metadata("test_user", "run_fetcher", 4))
    demog_2_td.append_data({"country": "Kenya"}, Metadata("test_user", "demog_cleaner", 5))

    message_td.append_traced_data("demog_1", demog_1_td, Metadata("test_user", "demog_1_append", 6))
    message_td.append_traced_data("demog_2", demog_2_td, Metadata("test_user", "demog_2_append", 7))

    return message_td


class TestTracedDataCSVIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_export_traced_data_iterable_to_csv(self):
        file_path = path.join(self.test_dir, "csv_test.csv")

        # Test exporting wrong data type
        data = list(generate_traced_data_iterable())
        with open(file_path, "w") as f:
            try:
                TracedDataCSVIO.export_traced_data_iterable_to_csv(data[0], f)
                self.fail("Exporting the wrong data type did not raise an assertion error")
            except AssertionError as e:
                self.assertEquals(str(e), _td_type_error_string)

        # Test exporting normal data, including requesting an unknown header.
        data = generate_traced_data_iterable()
        with open(file_path, "w") as f:
            TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=["URN", "Gender", "Non-Existent"])

        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/csv_export_expected.csv"))

    def test_import_csv_to_traced_data_iterable(self):
        file_path = "tests/traced_data/resources/csv_import_data.csv"

        with open(file_path, "r") as f:
            exported = list(generate_traced_data_iterable())
            imported = list(TracedDataCSVIO.import_csv_to_traced_data_iterable("test_user", f))

            self.assertEqual(len(exported), len(imported))

            for x, y in zip(exported, imported):
                self.assertSetEqual(set(x.items()), set(y.items()))


class TestTracedDataJsonIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_export_traced_data_iterable_to_json(self):
        file_path = path.join(self.test_dir, "json_test.json")

        # Test exporting wrong data type
        data = list(generate_traced_data_iterable())
        with open(file_path, "w") as f:
            try:
                TracedDataJsonIO.export_traced_data_iterable_to_json(data[0], f)
                self.fail("Exporting the wrong data type did not raise an assertion error")
            except AssertionError as e:
                self.assertEquals(str(e), _td_type_error_string)

        # Test normal export
        data = generate_traced_data_iterable()
        with open(file_path, "w") as f:
            TracedDataJsonIO.export_traced_data_iterable_to_json(data, f)
        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/json_export_expected.json"))

        # Test normal export with pretty print enabled
        data = generate_traced_data_iterable()
        with open(file_path, "w") as f:
            TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)
        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/json_export_expected_pretty_print.json"))

        # Test export for appended TracedData
        data = [generate_appended_traced_data()]
        with open(file_path, "w") as f:
            TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)
        self.assertTrue(filecmp.cmp(
                file_path, "tests/traced_data/resources/json_export_expected_append_traced_data_pretty_print.json"
            ))

    def test_import_json_to_traced_data_iterable(self):
        # Test simple TracedData case
        file_path = "tests/traced_data/resources/json_export_expected.json"
        expected = list(generate_traced_data_iterable())

        with open(file_path, "r") as f:
            imported = list(TracedDataJsonIO.import_json_to_traced_data_iterable(f))

        self.assertListEqual(expected, imported)

        # Test appended TracedData case
        file_path = "tests/traced_data/resources/json_export_expected_append_traced_data_pretty_print.json"
        expected = [generate_appended_traced_data()]

        with open(file_path, "r") as f:
            imported = list(TracedDataJsonIO.import_json_to_traced_data_iterable(f))

        self.assertListEqual(expected, imported)


class TestTracedDataTheInterfaceIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_export_traced_data_iterable_to_the_interface(self):
        output_directory = self.test_dir

        data_dicts = [
            {"uuid": "a", "message": "Message 1", "date": "2018-06-01T10:47:02+03:00", "gender": "male",
             "age": 27, "county": None},
            {"uuid": "b", "message": "Message 2\nis very long", "date": "2018-05-30T21:00:00+03:00",
             "gender": None, "age": None},
            {"uuid": "c", "message": u"Message 3, has punctuation and non-ASCII: ø. These need cleaning!",
             "date": "2018-06-02T18:30:02+01:00", "county": "mogadishu"}
        ]

        data = map(
            lambda d: TracedData(d, Metadata("test_user", Metadata.get_call_location(), time.time())), data_dicts)

        TracedDataTheInterfaceIO.export_traced_data_iterable_to_the_interface(
            data, output_directory, "uuid",
            message_key="message", date_key="date",
            gender_key="gender", age_key="age", county_key="county")

        self.assertTrue(filecmp.cmp(path.join(output_directory, "inbox"),
                                    "tests/traced_data/resources/the_interface_export_expected_inbox"))
        self.assertTrue(filecmp.cmp(path.join(output_directory, "demo"),
                                    "tests/traced_data/resources/the_interface_export_expected_demo"))

    def test_export_traced_data_iterable_to_the_interface_with_tagging(self):
        output_directory = self.test_dir

        data_dicts = [
            {"uuid": "a", "date": "2018-06-01T10:47:02+03:00", "key_1": "ABC"},
            {"uuid": "b", "date": "2018-06-13T00:00:00+03:00", "key_1": u"cD: øe"}
        ]

        data = map(
            lambda d: TracedData(d, Metadata("test_user", Metadata.get_call_location(), time.time())), data_dicts)

        TracedDataTheInterfaceIO.export_traced_data_iterable_to_the_interface(
            data, output_directory, "uuid",
            message_key="key_1", tag_messages=True, date_key="date",
            gender_key="gender", age_key="age", county_key="county")

        self.assertTrue(filecmp.cmp(path.join(output_directory, "inbox"),
                                    "tests/traced_data/resources/the_interface_export_expected_tagged_inbox"))
        self.assertTrue(filecmp.cmp(path.join(output_directory, "demo"),
                                    "tests/traced_data/resources/the_interface_export_expected_tagged_demo"))

    def test_export_traced_data_iterable_to_the_interface_multiple_sender_messages(self):
        output_directory = self.test_dir

        data_dicts = [
            {"uuid": "a", "date": "2018-06-01T10:47:02+03:00", "message": "message 1"},
            {"uuid": "b", "date": "2018-06-13T00:00:00+03:00", "message": u"cD: øe"},
            {"uuid": "a", "date": "2018-06-01T10:50:00+03:00", "message": "message 2"}
        ]

        data = map(
            lambda d: TracedData(d, Metadata("test_user", Metadata.get_call_location(), time.time())), data_dicts)

        TracedDataTheInterfaceIO.export_traced_data_iterable_to_the_interface(
            data, output_directory, "uuid",
            message_key="message", tag_messages=True, date_key="date",
            gender_key="gender", age_key="age", county_key="county")

        self.assertTrue(filecmp.cmp(path.join(output_directory, "inbox"),
                                    "tests/traced_data/resources/the_interface_export_expected_multiple_inbox"))
        self.assertTrue(filecmp.cmp(path.join(output_directory, "demo"),
                                    "tests/traced_data/resources/the_interface_export_expected_multiple_demo"))
