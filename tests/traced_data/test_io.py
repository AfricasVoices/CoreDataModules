# coding=utf-8
import collections
import filecmp
import json
import shutil
import tempfile
import time
import unittest
from os import path
from unittest import mock

from core_data_modules.cleaners import Codes, english
from core_data_modules.cleaners.cleaning_utils import CleaningUtils
from core_data_modules.data_models import Scheme
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataCSVIO, TracedDataJsonIO, \
    _td_type_error_string, TracedDataCodaV2IO


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


class TestTracedDataCodaV2IO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_export_import_one_single_coded_scheme(self):
        file_path = path.join(self.test_dir, "coda_2_test.json")

        # Build raw input data
        message_dicts = [
            {"gender_raw": "woman", "gender_sent_on": "2018-11-01T07:13:04+03:00"},
            {"gender_raw": "", "gender_sent_on": "2018-11-01T07:17:04+03:00"},
            {"gender_raw": "hiya", "gender_sent_on": "2018-11-01T07:19:04+05:00"},
            {},
            {"gender_raw": "boy", "gender_sent_on": "2018-11-02T19:00:29+03:00"},
            {"gender_raw": "man", "gender_sent_on": "2018-11-02T19:00:29+03:00"},
        ]
        messages = [TracedData(d, Metadata("test_user", Metadata.get_call_location(), i))
                    for i, d in enumerate(message_dicts)]

        # Add message ids
        TracedDataCodaV2IO.compute_message_ids("test_user", messages, "gender_raw", "gender_coda_id")

        # Load gender scheme
        with open("tests/traced_data/resources/coda_2_gender_scheme.json") as f:
            gender_scheme = Scheme.from_firebase_map(json.load(f))

        # Apply the English gender cleaner
        with mock.patch("core_data_modules.util.TimeUtils.utc_now_as_iso_string") as time_mock, \
                mock.patch("core_data_modules.traced_data.Metadata.get_function_location") as location_mock:
            time_mock.return_value = "2018-11-02T15:00:07+00:00"
            location_mock.return_value = "english.DemographicCleaner.clean_gender"

            CleaningUtils.apply_cleaner_to_traced_data_iterable(
                "test_user", messages, "gender_raw", "gender_coded",
                english.DemographicCleaner.clean_gender, gender_scheme
            )

        # Export to a Coda 2 messages file
        with open(file_path, "w") as f:
            TracedDataCodaV2IO.export_traced_data_iterable_to_coda_2(
                messages, "gender_raw", "gender_sent_on", "gender_coda_id", {"gender_coded": gender_scheme}, f)

        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_2_export_expected_one_scheme.json"))

        # Test importing with no file available
        imported_messages = []
        for td in messages:
            imported_messages.append(td.copy())
        TracedDataCodaV2IO.import_coda_2_to_traced_data_iterable(
            "test_user", imported_messages, "gender_coda_id", {"gender_coded": gender_scheme})
        # Deliberately testing the read can be done twice
        TracedDataCodaV2IO.import_coda_2_to_traced_data_iterable(
            "test_user", imported_messages, "gender_coda_id", {"gender_coded": gender_scheme})

        na_id = gender_scheme.get_code_with_control_code(Codes.TRUE_MISSING).code_id
        nr_id = gender_scheme.get_code_with_control_code(Codes.NOT_REVIEWED).code_id

        # Set TRUE_MISSING codes
        for td in imported_messages:
            na_label = CleaningUtils.make_label_from_cleaner_code(
                gender_scheme,
                gender_scheme.get_code_with_control_code(Codes.TRUE_MISSING),
                "test_export_traced_data_iterable_to_coda_2",
                date_time_utc="2018-11-02T10:00:00+00:00"
            )
            if td.get("gender_raw", "") == "":
                td.append_data({"gender_coded": na_label.to_dict()},
                               Metadata("test_user", Metadata.get_call_location(), time.time()))

        imported_code_ids = [td["gender_coded"]["CodeID"] for td in imported_messages]

        self.assertListEqual(imported_code_ids, [nr_id, na_id, nr_id, na_id, nr_id, nr_id])

        # Test importing from the test file
        imported_messages = []
        for td in messages:
            imported_messages.append(td.copy())
        with open("tests/traced_data/resources/coda_2_import_test_one_scheme.json", "r") as f:
            TracedDataCodaV2IO.import_coda_2_to_traced_data_iterable(
                "test_user", imported_messages, "gender_coda_id", {"gender_coded": gender_scheme}, f)

        # Set TRUE_MISSING codes
        for td in imported_messages:
            na_label = CleaningUtils.make_label_from_cleaner_code(
                gender_scheme,
                gender_scheme.get_code_with_control_code(Codes.TRUE_MISSING),
                "test_export_traced_data_iterable_to_coda_2",
                date_time_utc="2018-11-02T10:00:00+00:00"
            )
            if td.get("gender_raw", "") == "":
                td.append_data({"gender_coded": na_label.to_dict()},
                               Metadata("test_user", Metadata.get_call_location(), time.time()))

        imported_code_ids = [td["gender_coded"]["CodeID"] for td in imported_messages]

        expected_code_ids = [
            gender_scheme.get_code_with_match_value("female").code_id,  # Manually approved auto-code
            gender_scheme.get_code_with_control_code(Codes.TRUE_MISSING).code_id,  # Empty raw message
            gender_scheme.get_code_with_control_code(Codes.NOT_REVIEWED).code_id,  # Manually assigned code which isn't checked
            gender_scheme.get_code_with_control_code(Codes.TRUE_MISSING).code_id,  # No raw message
            gender_scheme.get_code_with_control_code(Codes.NOT_CODED).code_id,  # Manually Not Coded
            gender_scheme.get_code_with_control_code(Codes.NOT_REVIEWED).code_id,  # Manually un-coded
        ]
        self.assertListEqual(imported_code_ids, expected_code_ids)

        # Add an element with the same raw text but a conflicting
        messages.append(TracedData({
            "gender_raw": "woman", "gender_sent_on": "2018-11-01T07:13:04+03:00",
            "gender_coded": CleaningUtils.make_label_from_cleaner_code(
                gender_scheme, gender_scheme.get_code_with_match_value("male"), "make_location_label",
                date_time_utc="2018-11-03T13:40:50Z").to_dict()
        }, Metadata("test_user", Metadata.get_call_location(), time.time())))
        TracedDataCodaV2IO.compute_message_ids("test_user", messages, "gender_raw", "gender_coda_id")

        with open(file_path, "w") as f:
            try:
                TracedDataCodaV2IO.export_traced_data_iterable_to_coda_2(
                    messages, "gender_raw", "gender_sent_on", "gender_coda_id", {"gender_coded": gender_scheme}, f)
            except AssertionError as e:
                assert str(e) == "Messages with the same id " \
                                 "(cf2e5bff1ef03dcd20d1a0b18ef7d89fc80a3554434165753672f6f40fde1d25) have different " \
                                 "labels for coded_key 'gender_coded'"
                return
            self.fail("Exporting data with conflicting labels did not fail")

    def test_export_two_single_coded_schemes(self):
        file_path = path.join(self.test_dir, "coda_2_test.json")

        # Load schemes
        with open("tests/traced_data/resources/coda_2_district_scheme.json") as f:
            district_scheme = Scheme.from_firebase_map(json.load(f))

        with open("tests/traced_data/resources/coda_2_zone_scheme.json") as f:
            zone_scheme = Scheme.from_firebase_map(json.load(f))

        def make_location_label(scheme, value):
            if value in {Codes.TRUE_MISSING, Codes.SKIPPED, Codes.NOT_CODED}:
                code = scheme.get_code_with_control_code(value)
            else:
                code = scheme.get_code_with_match_value(value)

            return CleaningUtils.make_label_from_cleaner_code(scheme, code, "make_location_label",
                                                              date_time_utc="2018-11-02T13:40:50Z").to_dict()

        # Build raw input data
        message_dicts = [
            # Normal, coded data
            {"location_raw": "mog", "location_sent_on": "2018-11-01T07:13:04+03:00",
             "district": make_location_label(district_scheme, "mogadishu"),
             "zone": make_location_label(zone_scheme, "scz")},

            # Data coded under one scheme only
            {"location_raw": "kismayo", "location_sent_on": "2018-11-01T07:17:04+03:00",
             "district": make_location_label(district_scheme, "kismayo")},

            # Data coded as missing under both schemes
            {"location_raw": "", "location_sent_on": "2018-11-01T07:19:04+05:00",
             "district": make_location_label(district_scheme, Codes.TRUE_MISSING),
             "zone": make_location_label(zone_scheme, Codes.TRUE_MISSING)},

            # No data
            {},

            # Data coded as NC under both schemes
            {"location_raw": "kismyo", "location_sent_on": "2018-11-01T07:19:30+03:00",
             "district": make_location_label(district_scheme, Codes.NOT_CODED),
             "zone": make_location_label(zone_scheme, Codes.NOT_CODED)},

            # Data coded as NC under one scheme only
            {"location_raw": "kismay", "location_sent_on": "2018-11-01T07:19:30+03:00",
             "district": make_location_label(district_scheme, "kismayo"),
             "zone": make_location_label(zone_scheme, Codes.NOT_CODED)},
        ]
        messages = [TracedData(d, Metadata("test_user", Metadata.get_call_location(), i))
                    for i, d in enumerate(message_dicts)]

        # Add message ids
        TracedDataCodaV2IO.compute_message_ids("test_user", messages, "location_raw", "location_coda_id")

        # Export to a Coda 2 messages file
        with open(file_path, "w") as f:
            scheme_key_map = collections.OrderedDict()  # Using OrderedDict to make tests easier to write in Py2 and Py3.
            scheme_key_map["district"] = district_scheme
            scheme_key_map["zone"] = zone_scheme

            TracedDataCodaV2IO.export_traced_data_iterable_to_coda_2(
                messages, "location_raw", "location_sent_on", "location_coda_id", scheme_key_map, f)

        self.assertTrue(
            filecmp.cmp(file_path, "tests/traced_data/resources/coda_2_export_expected_multiple_schemes.json"))

    def test_export_import_one_multi_coded_scheme(self):
        file_path = path.join(self.test_dir, "coda_2_test.json")

        # Build raw input data
        message_dicts = [
            {"msg_raw": "food", "msg_sent_on": "2018-11-01T07:13:04+03:00"},
            {"msg_raw": "", "msg_sent_on": "2018-11-01T07:17:04+03:00"},
            {"msg_raw": "food + water", "msg_sent_on": "2018-11-01T07:19:04+05:00"},
            {},
            {"msg_raw": "water", "msg_sent_on": "2018-11-02T19:00:29+03:00"},
            {"msg_raw": "abcd", "msg_sent_on": "2018-11-02T20:30:45+03:00"}
        ]
        messages = [TracedData(d, Metadata("test_user", Metadata.get_call_location(), i))
                    for i, d in enumerate(message_dicts)]

        # Add message ids
        TracedDataCodaV2IO.compute_message_ids("test_user", messages, "msg_raw", "msg_coda_id")

        # Load gender scheme
        with open("tests/traced_data/resources/coda_2_msg_scheme.json") as f:
            msg_scheme = Scheme.from_firebase_map(json.load(f))

        # Export to a Coda 2 messages file
        with open(file_path, "w") as f:
            TracedDataCodaV2IO.export_traced_data_iterable_to_coda_2(
                messages, "msg_raw", "msg_sent_on", "msg_coda_id", {"msg_coded": msg_scheme}, f)

        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_2_export_expected_multi_coded.json"))

        # Test importing with no file available
        imported_messages = []
        for td in messages:
            imported_messages.append(td.copy())
        TracedDataCodaV2IO.import_coda_2_to_traced_data_iterable_multi_coded(
            "test_user", imported_messages, "msg_coda_id", {"msg_coded": msg_scheme})
        # Deliberately testing the read can be done twice
        TracedDataCodaV2IO.import_coda_2_to_traced_data_iterable_multi_coded(
            "test_user", imported_messages, "msg_coda_id", {"msg_coded": msg_scheme})

        na_id = msg_scheme.get_code_with_control_code(Codes.TRUE_MISSING).code_id
        nr_id = msg_scheme.get_code_with_control_code(Codes.NOT_REVIEWED).code_id

        # Set TRUE_MISSING codes
        for td in imported_messages:
            na_label = CleaningUtils.make_label_from_cleaner_code(
                msg_scheme,
                msg_scheme.get_code_with_control_code(Codes.TRUE_MISSING),
                "test_export_traced_data_iterable_to_coda_2",
                date_time_utc="2018-11-02T10:00:00+00:00"
            )
            if td.get("msg_raw", "") == "":
                td.append_data({"msg_coded": [na_label.to_dict()]},
                               Metadata("test_user", Metadata.get_call_location(), time.time()))

        for td in imported_messages:
            self.assertEqual(len(td["msg_coded"]), 1)
        imported_code_ids = [td["msg_coded"][0]["CodeID"] for td in imported_messages]
        self.assertListEqual(imported_code_ids, [nr_id, na_id, nr_id, na_id, nr_id, nr_id])

        # Test importing from the test file
        imported_messages = []
        for td in messages:
            imported_messages.append(td.copy())
        with open("tests/traced_data/resources/coda_2_import_test_multi_coded.json", "r") as f:
            TracedDataCodaV2IO.import_coda_2_to_traced_data_iterable_multi_coded(
                "test_user", imported_messages, "msg_coda_id", {"msg_coded": msg_scheme}, f)

        # Set TRUE_MISSING codes
        for td in imported_messages:
            na_label = CleaningUtils.make_label_from_cleaner_code(
                msg_scheme,
                msg_scheme.get_code_with_control_code(Codes.TRUE_MISSING),
                "test_export_traced_data_iterable_to_coda_2",
                date_time_utc="2018-11-02T10:00:00+00:00"
            )
            if td.get("msg_raw", "") == "":
                td.append_data({"msg_coded": [na_label.to_dict()]},
                               Metadata("test_user", Metadata.get_call_location(), time.time()))

        imported_code_ids = []
        for td in imported_messages:
            imported_code_ids.append([code["CodeID"] for code in td["msg_coded"]])

        expected_code_ids = [
            {msg_scheme.get_code_with_match_value("food").code_id},
            {msg_scheme.get_code_with_control_code(Codes.TRUE_MISSING).code_id},
            {msg_scheme.get_code_with_match_value("food").code_id, msg_scheme.get_code_with_match_value("water").code_id},
            {msg_scheme.get_code_with_control_code(Codes.TRUE_MISSING).code_id},
            {msg_scheme.get_code_with_match_value("water").code_id},
            {msg_scheme.get_code_with_control_code(Codes.NOT_CODED).code_id}
        ]

        for x, y in zip(imported_code_ids, expected_code_ids):
            self.assertSetEqual(set(x), set(y))


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
