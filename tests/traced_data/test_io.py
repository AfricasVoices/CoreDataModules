# coding=utf-8
import collections
import filecmp
import json
import shutil
import tempfile
import time
import unittest
from os import path

try:
    from unittest import mock  # Python 3.3+
except ImportError:
    import mock  # Other versions

from core_data_modules.cleaners import Codes, english
from core_data_modules.cleaners.cleaning_utils import CleaningUtils
from core_data_modules.data_models import Scheme
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataCodaIO, TracedDataCSVIO, TracedDataJsonIO, \
    TracedDataTheInterfaceIO, _td_type_error_string, TracedDataCoda2IO


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


class TestTracedDataCodaIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_export_traced_data_iterable_to_coda(self):
        file_path = path.join(self.test_dir, "coda_test.csv")

        # Test exporting wrong data type
        data = list(generate_traced_data_iterable())
        with open(file_path, "w") as f:
            try:
                TracedDataCodaIO.export_traced_data_iterable_to_coda(data[0], "Gender", f)
                self.fail("Exporting the wrong data type did not raise an assertion error")
            except AssertionError as e:
                self.assertEquals(str(e), _td_type_error_string)

        # Test exporting everything
        data = generate_traced_data_iterable()
        with open(file_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda(data, "Gender", f)
        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output_coded.csv"))

        # Test exporting only not coded elements
        data = list(generate_traced_data_iterable())
        data[0].append_data({"Gender_clean": Codes.NOT_CODED}, Metadata("test_user", "cleaner", 10))
        data[2].append_data({"Gender_clean": "F"}, Metadata("test_user", "cleaner", 11))
        data[4].append_data({"Gender_clean": "F"}, Metadata("test_user", "cleaner", 12))
        with open(file_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda(
                data, "Gender", f, exclude_coded_with_key="Gender_clean")
        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output_not_coded.csv"))

        # Test that missing data is not exported
        data = list(generate_traced_data_iterable())
        missing_td = TracedData({"Gender": Codes.TRUE_MISSING},
                                Metadata("test_user", Metadata.get_call_location(), time.time()))
        data.insert(2, missing_td)
        with open(file_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda(
                data, "Gender", f, exclude_coded_with_key="Gender_clean")
        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output_missing.csv"))

    def test_export_traced_data_iterable_to_coda_with_scheme(self):
        file_path = path.join(self.test_dir, "coda_test_with_codes.csv")

        data = list(generate_traced_data_iterable())
        data[0].append_data({"Gender_clean": "F"}, Metadata("test_user", "cleaner", 11))
        data[1].append_data({"Gender_clean": "M"}, Metadata("test_user", "cleaner", 12))
        data[2].append_data({"Gender_clean": "F"}, Metadata("test_user", "cleaner", 13))
        data[4].append_data({"Gender_clean": "F"}, Metadata("test_user", "cleaner", 14))

        # Test exporting wrong data type
        with open(file_path, "w") as f:
            try:
                TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                    data[0], "Gender", {"Gender": "Gender_clean"}, f)
                self.fail("Exporting the wrong data type did not raise an assertion error")
            except AssertionError as e:
                self.assertEquals(str(e), _td_type_error_string)

        # Test normal export with specified key
        with open(file_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                data, "Gender", {"Gender": "Gender_clean"}, f)
        self.assertTrue(
            filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_output_with_codes.csv"))

        # Test updating a file with multiple code schemes
        prev_file_path = path.join("tests/traced_data/resources/coda_export_for_append_multiple_schemes.csv")
        extended_file_path = file_path
        with open(extended_file_path, "w") as f, open(prev_file_path, "r") as prev_f:
            try:
                TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                    data, "Gender", {"Gender": "Gender_clean"}, f, prev_f)
            except AssertionError as e:
                self.assertEquals(str(e), "Cannot import a Coda file with multiple scheme ids")
        # Test updating a file with new codes.
        prev_file_path = path.join("tests/traced_data/resources/coda_export_for_append.csv")
        extended_file_path = file_path

        data.append(TracedData(
            {"URN": "+0012345000008", "Gender": "girl", "Gender_clean": "f"},
            Metadata("test_user", "data_generator", 10)
        ))
        data.append(TracedData(
            {"URN": "+0012345000008", "Gender": "27"},
            Metadata("test_user", "data_generator", 10)
        ))

        with open(extended_file_path, "w") as f, open(prev_file_path, "r") as prev_f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                data, "Gender", {"Gender": "Gender_clean"}, f, prev_f)
        self.assertTrue(filecmp.cmp(extended_file_path, "tests/traced_data/resources/coda_export_expected_append.csv"))

        # Test exporting with conflicting codes
        data[4].append_data({"Gender_clean": "M"}, Metadata("test_user", "cleaner", 15))
        with open(file_path, "w") as f:
            try:
                TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                    data, "Gender", {"Gender": "Gender_clean"}, f)
                self.fail("Exporting conflicting codes did not raise an assertion error")
            except AssertionError as e:
                self.assertEquals(str(e), "Raw message 'female' not uniquely coded.")

        # Test exporting multiple code schemes
        data_dicts = [
            {"Value": "man", "Gender_clean": "male"},
            {"Value": "woman", "Gender_clean": "female"},
            {"Value": "twenty", "Age_clean": 20},
            {"Value": "hello"},
            {"Value": "44F", "Gender_clean": "female", "Age_clean": 44},
            {"Value": "33", "Age_clean": 33}
        ]
        data = [TracedData(d, Metadata("test_user", "data_generator", i)) for i, d in enumerate(data_dicts)]
        with open(file_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                data, "Value", {"Gender": "Gender_clean", "Age": "Age_clean"}, f)
        self.assertTrue(
            filecmp.cmp(file_path, "tests/traced_data/resources/coda_export_expected_multiple_schemes.csv"))

    def test_import_coda_to_traced_data_iterable(self):
        # Test single schemes, with and without overwrite_existing_codes set to True
        self._overwrite_is_false_asserts()
        self._overwrite_is_true_asserts()

        # Test importing multiple code schemes
        data_dicts = [
            {"Value": "man", "Gender_clean": "female"},
            {"Value": "woman"},
            {"Value": "twenty", "Age_clean": 20},
            {"Value": "hello"},
            {"Value": "44F", "Gender_clean": "female", "Age_clean": 4},
            {"Value": Codes.TRUE_MISSING},
            {"Value": Codes.SKIPPED},
            {"Value": Codes.NOT_INTERNALLY_CONSISTENT},
            {"Value": "33", "Age_clean": 33}
        ]
        data = [TracedData(d, Metadata("test_user", "data_generator", i)) for i, d in enumerate(data_dicts)]
        with open("tests/traced_data/resources/coda_export_expected_multiple_schemes.csv", "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
               "test_user", data, "Value", {"Gender": "Gender_clean", "Age": "Age_clean"}, f, True)

        expected_data_dicts = [
            {"Value": "man", "Gender_clean": "male", "Age_clean": Codes.NOT_REVIEWED},
            {"Value": "woman", "Gender_clean": "female", "Age_clean": Codes.NOT_REVIEWED},
            {"Value": "twenty", "Gender_clean": Codes.NOT_REVIEWED, "Age_clean": "20"},
            {"Value": "hello", "Gender_clean": Codes.NOT_REVIEWED, "Age_clean": Codes.NOT_REVIEWED},
            {"Value": "44F", "Gender_clean": "female", "Age_clean": "44"},
            {"Value": Codes.TRUE_MISSING, "Gender_clean": Codes.TRUE_MISSING, "Age_clean": Codes.TRUE_MISSING},
            {"Value": Codes.SKIPPED, "Gender_clean": Codes.SKIPPED, "Age_clean": Codes.SKIPPED},
            {"Value": Codes.NOT_INTERNALLY_CONSISTENT, "Gender_clean": Codes.NOT_INTERNALLY_CONSISTENT,
             "Age_clean": Codes.NOT_INTERNALLY_CONSISTENT},
            {"Value": "33", "Gender_clean": Codes.NOT_REVIEWED, "Age_clean": "33"}
        ]

        for imported_td, expected in zip(data, expected_data_dicts):
            self.assertDictEqual(dict(imported_td.items()), expected)

    def test_import_coda_to_traced_data_iterable_as_matrix(self):
        # TODO: Move this function to below self._overwrite_is_true_asserts
        # Test normal usage
        responses = ["AC", "B", "Z", "CB"]
        data = [TracedData({"Response": response}, Metadata("test_user", Metadata.get_call_location(), time.time()))
                for response in responses]

        with open("tests/traced_data/resources/coda_import_as_matrix_data.csv", "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable_as_matrix(
                "test_user", data, "Response", {"Reason 1", "Reason 2"}, f)

        expected_data_dicts = [
            {"Response": "AC", "a": Codes.MATRIX_1, "b": Codes.MATRIX_0, "c": Codes.MATRIX_1, Codes.NOT_REVIEWED: Codes.MATRIX_0},
            {"Response": "B",  "a": Codes.MATRIX_0, "b": Codes.MATRIX_1, "c": Codes.MATRIX_0, Codes.NOT_REVIEWED: Codes.MATRIX_0},
            {"Response": "Z",  "a": Codes.MATRIX_0, "b": Codes.MATRIX_0, "c": Codes.MATRIX_0, Codes.NOT_REVIEWED: Codes.MATRIX_1},
            {"Response": "CB", "a": Codes.MATRIX_0, "b": Codes.MATRIX_1, "c": Codes.MATRIX_1, Codes.NOT_REVIEWED: Codes.MATRIX_0}
        ]

        for imported_td, expected in zip(data, expected_data_dicts):
            self.assertDictEqual(dict(imported_td.items()), expected)

        # Test setting a prefix
        responses = ["AC", "B", "Z", "CB"]
        data = [TracedData({"Response": response}, Metadata("test_user", Metadata.get_call_location(), time.time()))
                for response in responses]

        with open("tests/traced_data/resources/coda_import_as_matrix_data.csv", "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable_as_matrix(
                "test_user", data, "Response", {"Reason 1", "Reason 2"}, f, "response_coded_")

        nr_key = "response_coded_{}".format(Codes.NOT_REVIEWED)
        expected_data_dicts = [
            {"Response": "AC", "response_coded_a": Codes.MATRIX_1, "response_coded_b": Codes.MATRIX_0, "response_coded_c": Codes.MATRIX_1, nr_key: Codes.MATRIX_0},
            {"Response": "B",  "response_coded_a": Codes.MATRIX_0, "response_coded_b": Codes.MATRIX_1, "response_coded_c": Codes.MATRIX_0, nr_key: Codes.MATRIX_0},
            {"Response": "Z",  "response_coded_a": Codes.MATRIX_0, "response_coded_b": Codes.MATRIX_0, "response_coded_c": Codes.MATRIX_0, nr_key: Codes.MATRIX_1},
            {"Response": "CB", "response_coded_a": Codes.MATRIX_0, "response_coded_b": Codes.MATRIX_1, "response_coded_c": Codes.MATRIX_1, nr_key: Codes.MATRIX_0}
        ]

        for imported_td, expected in zip(data, expected_data_dicts):
            self.assertDictEqual(dict(imported_td.items()), expected)

        # TODO: Test optional overwrite_existing_codes flag if we decide to implement.

    def _overwrite_is_false_asserts(self):
        data = list(generate_traced_data_iterable())
        data[0].append_data({"Gender_clean": "X"}, Metadata("test_user", "cleaner", 20))

        file_path = "tests/traced_data/resources/coda_import_data.csv"
        with open(file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                "test_user", data, "Gender", {"CodaCodedGender": "Gender_clean"}, f)

        expected_data = [
            {"URN": "+0012345000000", "Gender": "female", "Gender_clean": "X"},
            {"URN": "+0012345000001", "Gender": "m", "Gender_clean": "M"},
            {"URN": "+0012345000002", "Gender": "WoMaN", "Gender_clean": "F"},
            {"URN": "+0012345000003", "Gender": "27", "Gender_clean": Codes.NOT_REVIEWED},
            {"URN": "+0012345000004", "Gender": "female", "Gender_clean": "F"}
        ]

        self.assertEqual(len(data), len(expected_data))

        for x, y in zip(data, expected_data):
            self.assertDictEqual(dict(x.items()), y)

    def _overwrite_is_true_asserts(self):
        data = list(generate_traced_data_iterable())
        data[0].append_data({"Gender_clean": "X"}, Metadata("test_user", "cleaner", 20))

        file_path = "tests/traced_data/resources/coda_import_data.csv"
        with open(file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                "test_user", data, "Gender", {"CodaCodedGender": "Gender_clean"}, f, True)

        expected_data = [
            {"URN": "+0012345000000", "Gender": "female", "Gender_clean": "F"},
            {"URN": "+0012345000001", "Gender": "m", "Gender_clean": "M"},
            {"URN": "+0012345000002", "Gender": "WoMaN", "Gender_clean": "F"},
            {"URN": "+0012345000003", "Gender": "27", "Gender_clean": Codes.NOT_REVIEWED},
            {"URN": "+0012345000004", "Gender": "female", "Gender_clean": "F"}
        ]

        self.assertEqual(len(data), len(expected_data))

        for x, y in zip(data, expected_data):
            self.assertDictEqual(dict(x.items()), y)


class TestTracedDataCoda2IO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_one_scheme(self):
        file_path = path.join(self.test_dir, "coda_2_test.json")

        # Build raw input data
        message_dicts = [
            {"gender_raw": "woman", "gender_sent_on": "2018-11-01T07:13:04+03:00"},
            {"gender_raw": "", "gender_sent_on": "2018-11-01T07:17:04+03:00"},
            {"gender_raw": "hiya", "gender_sent_on": "2018-11-01T07:19:04+05:00"},
            {},
            {"gender_raw": "boy", "gender_sent_on": "2018-11-02T19:00:29+03:00"},
        ]
        messages = [TracedData(d, Metadata("test_user", Metadata.get_call_location(), i))
                    for i, d in enumerate(message_dicts)]

        # Add message ids
        TracedDataCoda2IO.add_message_ids("test_user", messages, "gender_raw", "gender_coda_id")

        # Load gender scheme
        with open("tests/traced_data/resources/coda_2_gender_scheme.json") as f:
            gender_scheme = Scheme.from_firebase_map(json.load(f))

        # Set TRUE_MISSING codes
        for td in messages:
            na_label = CleaningUtils.make_label_from_cleaner_code(
                gender_scheme,
                gender_scheme.get_code_with_control_code(Codes.TRUE_MISSING),
                "test_export_traced_data_iterable_to_coda_2",
                date_time_utc="2018-11-02T10:00:00+00:00"
            )
            if td.get("gender_raw", "") == "":
                td.append_data({"gender_coded": na_label.to_dict()},
                               Metadata("test_user", Metadata.get_call_location(), time.time()))

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
            TracedDataCoda2IO.export_traced_data_iterable_to_coda_2(
                messages, "gender_raw", "gender_sent_on", "gender_coda_id", {"gender_coded": gender_scheme}, f)

        self.assertTrue(filecmp.cmp(file_path, "tests/traced_data/resources/coda_2_export_expected_one_scheme.json"))

        # Test importing with no file available
        imported_messages = []
        for td in messages:
            imported_messages.append(td.copy())
        TracedDataCoda2IO.import_coda_2_to_traced_data_iterable(
            "test_user", imported_messages, "gender_coda_id", {"gender_coded": gender_scheme})

        na_id = gender_scheme.get_code_with_control_code(Codes.TRUE_MISSING).code_id
        nr_id = gender_scheme.get_code_with_control_code(Codes.NOT_REVIEWED).code_id
        imported_code_ids = [td["gender_coded"]["CodeID"] for td in imported_messages]
        self.assertListEqual(imported_code_ids, [nr_id, na_id, nr_id, na_id, nr_id])

        # Add an element with the same raw text but a conflicting
        messages.append(TracedData({
            "gender_raw": "woman", "gender_sent_on": "2018-11-01T07:13:04+03:00",
            "gender_coded": CleaningUtils.make_label_from_cleaner_code(
                gender_scheme, gender_scheme.get_code_with_match_value("male"), "make_location_label",
                date_time_utc="2018-11-03T13:40:50Z").to_dict()
        }, Metadata("test_user", Metadata.get_call_location(), time.time())))
        TracedDataCoda2IO.add_message_ids("test_user", messages, "gender_raw", "gender_coda_id")

        with open(file_path, "w") as f:
            try:
                TracedDataCoda2IO.export_traced_data_iterable_to_coda_2(
                    messages, "gender_raw", "gender_sent_on", "gender_coda_id", {"gender_coded": gender_scheme}, f)
            except AssertionError as e:
                assert str(e) == "Messages with the same id " \
                                 "(cf2e5bff1ef03dcd20d1a0b18ef7d89fc80a3554434165753672f6f40fde1d25) have different " \
                                 "labels for coded_key 'gender_coded'"
                return
            self.fail("Exporting data with conflicting labels did not fail")

    def test_export_traced_data_iterable_to_coda_2_multiple_schemes(self):
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
        TracedDataCoda2IO.add_message_ids("test_user", messages, "location_raw", "location_coda_id")

        # Export to a Coda 2 messages file
        with open(file_path, "w") as f:
            scheme_keys = collections.OrderedDict()  # Using OrderedDict to make tests easier to write in Py2 and Py3.
            scheme_keys["district"] = district_scheme
            scheme_keys["zone"] = zone_scheme

            TracedDataCoda2IO.export_traced_data_iterable_to_coda_2(
                messages, "location_raw", "location_sent_on", "location_coda_id", scheme_keys, f)

        self.assertTrue(
            filecmp.cmp(file_path, "tests/traced_data/resources/coda_2_export_expected_multiple_schemes.json"))

        # Test ambiguous missing codes
        def test_ambiguous_missing_codes(d):
            # Test exporting with ambiguous missing codes
            conflicting_missings = list(messages)
            conflicting_missings.append(TracedData(d, Metadata("test_user", Metadata.get_call_location(), time.time())))
            TracedDataCoda2IO.add_message_ids("test_user", conflicting_missings, "location_raw", "location_coda_id")

            with open(file_path, "w") as f:
                try:
                    scheme_keys = collections.OrderedDict()
                    scheme_keys["district"] = district_scheme
                    scheme_keys["zone"] = zone_scheme

                    TracedDataCoda2IO.export_traced_data_iterable_to_coda_2(
                        conflicting_missings, "location_raw", "location_sent_on", "location_coda_id", scheme_keys, f)
                except AssertionError as e:
                    assert str(e) == "Data labelled as NA or NS under one code scheme but not all of the others"
                    return
                self.fail("Exporting data with ambiguous missing codes did not fail")

        test_ambiguous_missing_codes({
            "location_raw": "baidoa", "location_sent_on": "2018-11-01T07:19:30+03:00",
            "district": make_location_label(district_scheme, Codes.TRUE_MISSING),
            "zone": make_location_label(zone_scheme, Codes.NOT_CODED)
        })

        test_ambiguous_missing_codes({
            "location_raw": "baidoa", "location_sent_on": "2018-11-01T07:19:30+03:00",
            "district": make_location_label(district_scheme, Codes.TRUE_MISSING),
            "zone": make_location_label(zone_scheme, Codes.SKIPPED)
        })

        
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
