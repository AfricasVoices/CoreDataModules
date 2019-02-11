import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.util import FoldTracedData


class TestFoldTracedData(unittest.TestCase):
    @staticmethod
    def make_traced_data(dicts, start_time=0):
        return [TracedData(d, Metadata("test_user", Metadata.get_call_location(), i + start_time))
                for i, d in enumerate(dicts)]

    def test_group_by(self):
        flat_dicts = [
            {"id": "a", "x": "4"},
            {"id": "b", "x": "5"},
            {"id": "a", "x": "6"},
            {"id": "a", "x": "7"},
            {"id": "c", "x": "8"},
            {"id": "b", "x": "9"}
        ]

        flat_data = self.make_traced_data(flat_dicts)

        grouped = list(FoldTracedData.group_by(flat_data, lambda td: td["id"]))

        self.assertEqual(len(grouped), 3)

        grouped.sort(key=lambda l: l[0]["id"])
        self.assertListEqual([td["x"] for td in grouped[0]], ["4", "6", "7"])
        self.assertListEqual([td["x"] for td in grouped[1]], ["5", "9"])
        self.assertListEqual([td["x"] for td in grouped[2]], ["8"])

    def test_fold_groups(self):
        data = [TracedData({"x": c}, Metadata("test_user", Metadata.get_call_location(), i))
                for i, c in enumerate(["a", "b", "c", "d", "e"])]

        groups = [
            [data[0]],
            [data[1], data[2], data[3]],
            [data[4]]
        ]

        def fold_fn(td_1, td_2):
            td_1 = td_1.copy()
            td_2 = td_2.copy()

            folded_dict = {"x": "{}{}".format(td_1["x"], td_2["x"])}

            td_1.append_data(folded_dict, Metadata("test_user", Metadata.get_call_location(), 10))
            td_2.append_data(folded_dict, Metadata("test_user", Metadata.get_call_location(), 11))

            folded = td_1
            td_1.append_traced_data("folded_with", td_2, Metadata("test_user", Metadata.get_call_location(), 12))

            return folded

        folded_data = FoldTracedData.fold_groups(groups, fold_fn)

        self.assertDictEqual(dict(folded_data[0].items()), {"x": "a"})
        self.assertDictEqual(dict(folded_data[1].items()), {"x": "bcd"})
        self.assertDictEqual(dict(folded_data[2].items()), {"x": "e"})

    def test_assert_equal_keys_equal(self):
        td_1 = TracedData(
            {"eq1": "5", "eq2": "6", "ne": "10"},
            Metadata("test_user", Metadata.get_call_location(), 0)
        )

        td_2_expect_pass = TracedData(
            {"eq1": "5", "eq2": "6", "ne": "13"},
            Metadata("test_user", Metadata.get_call_location(), 1)
        )

        td_2_expect_fail = TracedData(
            {"eq1": "5", "eq2": "7", "ne": "10"},
            Metadata("test_user", Metadata.get_call_location(), 1)
        )

        # This test is considered successful if no assertion is raised
        FoldTracedData.assert_equal_keys_equal(td_1, td_2_expect_pass, {"eq1", "eq2"})

        try:
            FoldTracedData.assert_equal_keys_equal(td_1, td_2_expect_fail, {"eq1", "eq2"})
            self.fail("No AssertionError raised")
        except AssertionError as e:
            if str(e) == "No AssertionError raised":
                raise e

            self.assertEqual(str(e),
                             "Key 'eq2' should be the same in both td_1 and td_2 but is "
                             "different (has values '6' and '7' respectively)")

    def test_reconcile_missing_values(self):
        self.assertEqual(FoldTracedData.reconcile_missing_values(Codes.TRUE_MISSING, Codes.NOT_CODED), Codes.NOT_CODED)
        self.assertEqual(FoldTracedData.reconcile_missing_values(Codes.STOP, Codes.NOT_CODED), Codes.STOP)

    def test_reconcile_keys_by_concatenation(self):
        def make_tds():
            td_1 = TracedData(
                {"msg1": "abc", "msg2": "xy", "x": 4},
                Metadata("test_user", Metadata.get_call_location(), 0)
            )

            td_2 = TracedData(
                {"msg1": "def", "msg2": "xy", "x": 5},
                Metadata("test_user", Metadata.get_call_location(), 1)
            )

            return td_1, td_2

        td_1, td_2 = make_tds()
        FoldTracedData.reconcile_keys_by_concatenation("test_user", td_1, td_2, {"msg1", "msg2"})
        self.assertDictEqual(dict(td_1.items()), {"msg1": "abc;def", "msg2": "xy;xy", "x": 4})
        self.assertDictEqual(dict(td_2.items()), {"msg1": "abc;def", "msg2": "xy;xy", "x": 5})

        td_1, td_2 = make_tds()
        FoldTracedData.reconcile_keys_by_concatenation("test_user", td_1, td_2, {"msg1", "msg2"}, concat_delimiter="--")
        self.assertDictEqual(dict(td_1.items()), {"msg1": "abc--def", "msg2": "xy--xy", "x": 4})
        self.assertDictEqual(dict(td_2.items()), {"msg1": "abc--def", "msg2": "xy--xy", "x": 5})

    def test_reconcile_matrix_keys(self):
        td_1 = TracedData(
            {"a": Codes.MATRIX_0, "b": Codes.MATRIX_1, Codes.NOT_REVIEWED: Codes.MATRIX_1,
             Codes.NOT_CODED: Codes.MATRIX_1, "c": Codes.STOP},
            Metadata("test_user", Metadata.get_call_location(), 0)
        )

        td_2 = TracedData(
            {"a": Codes.MATRIX_0, "b": Codes.MATRIX_0, Codes.NOT_REVIEWED: Codes.MATRIX_0,
             Codes.NOT_CODED: Codes.MATRIX_0, "c": Codes.MATRIX_0},
            Metadata("test_user", Metadata.get_call_location(), 1)
        )

        # TODO: Update dictionaries above to test for the various cases of missing data

        FoldTracedData.reconcile_matrix_keys("test_user", td_1, td_2, td_1.keys())

        expected_dict = {"a": Codes.MATRIX_0, "b": Codes.MATRIX_1, Codes.NOT_REVIEWED: Codes.MATRIX_1,
                         Codes.NOT_CODED: Codes.MATRIX_0, "c": Codes.STOP}
        self.assertDictEqual(dict(td_1.items()), expected_dict)
        self.assertDictEqual(dict(td_2.items()), expected_dict)

    def test_reconcile_boolean_keys(self):
        td_1 = TracedData(
            {"a": Codes.TRUE, "b": Codes.FALSE, "c": Codes.FALSE, "d": Codes.NOT_CODED, "e": Codes.NOT_CODED},
            Metadata("test_user", Metadata.get_call_location(), 0)
        )

        td_2 = TracedData(
            {"a": Codes.TRUE, "b": Codes.TRUE, "c": Codes.FALSE, "d": Codes.TRUE, "e": Codes.NOT_CODED},
            Metadata("test_user", Metadata.get_call_location(), 1)
        )

        FoldTracedData.reconcile_boolean_keys("test_user", td_1, td_2, {"a", "b", "c", "d", "e"})

        expected_dict = {"a": Codes.TRUE, "b": Codes.TRUE, "c": Codes.FALSE, "d": Codes.TRUE, "e": Codes.FALSE}
        self.assertDictEqual(dict(td_1.items()), expected_dict)
        self.assertDictEqual(dict(td_2.items()), expected_dict)

    def test_reconcile_yes_no_keys(self):
        td_1 = TracedData(
            {"a": Codes.YES, "b": Codes.NO, "c": Codes.YES, "d": Codes.NO, "e": Codes.NOT_CODED, "f": Codes.NOT_CODED,
             "g": Codes.BOTH, "h": Codes.STOP},
            Metadata("test_user", Metadata.get_call_location(), 0)
        )

        td_2 = TracedData(
            {"a": Codes.YES, "b": Codes.YES, "c": Codes.NO, "d": Codes.NO, "e": Codes.YES, "f": Codes.NOT_CODED,
             "g": Codes.YES, "h": Codes.YES},
            Metadata("test_user", Metadata.get_call_location(), 1)
        )

        FoldTracedData.reconcile_yes_no_keys("test_user", td_1, td_2, {"a", "b", "c", "d", "e", "f", "g", "h"})

        expected_dict = {"a": Codes.YES, "b": Codes.BOTH, "c": Codes.BOTH, "d": Codes.NO, "e": Codes.YES,
                         "f": Codes.NOT_CODED, "g": Codes.BOTH, "h": Codes.STOP}
        self.assertDictEqual(dict(td_1.items()), expected_dict)
        self.assertDictEqual(dict(td_2.items()), expected_dict)

    def test_reconcile_binary_keys(self):
        td_1 = TracedData(
            {"a": "integrate", "b": "return", "c": FoldTracedData.AMBIVALENT_BINARY_VALUE,
             "d": FoldTracedData.AMBIVALENT_BINARY_VALUE, "e": "integrate",
             "f": Codes.NOT_CODED,
             "g": Codes.STOP, "h": Codes.NOT_CODED},
            Metadata("test_user", Metadata.get_call_location(), 0)
        )

        td_2 = TracedData(
            {"a": "integrate", "b": "integrate", "c": "return", "d": FoldTracedData.AMBIVALENT_BINARY_VALUE,
             "e": FoldTracedData.AMBIVALENT_BINARY_VALUE,
             "f": Codes.NOT_CODED,
             "g": Codes.NOT_CODED, "h": "integrate"},
            Metadata("test_user", Metadata.get_call_location(), 1)
        )

        FoldTracedData.reconcile_binary_keys("test_user", td_1, td_2, {"a", "b", "c", "d", "e", "f", "g", "h"})

        expected_dict = {"a": "integrate", "b": FoldTracedData.AMBIVALENT_BINARY_VALUE,
                         "c": FoldTracedData.AMBIVALENT_BINARY_VALUE, "d": FoldTracedData.AMBIVALENT_BINARY_VALUE,
                         "e": FoldTracedData.AMBIVALENT_BINARY_VALUE,
                         "f": Codes.NOT_CODED, "g": Codes.STOP, "h": "integrate"}

        self.assertDictEqual(dict(td_1.items()), expected_dict)
        self.assertDictEqual(dict(td_2.items()), expected_dict)

    def test_set_keys_to_value(self):
        td = TracedData(
            {"msg1": "abc", "msg2": "xy", "x": 4},
            Metadata("test_user", Metadata.get_call_location(), 0)
        )

        FoldTracedData.set_keys_to_value("test_user", td, {"msg1"})
        self.assertDictEqual(dict(td.items()), {"msg1": "MERGED", "msg2": "xy", "x": 4})

        FoldTracedData.set_keys_to_value("test_user", td, {"msg2", "x"}, value="----")
        self.assertDictEqual(dict(td.items()), {"msg1": "MERGED", "msg2": "----", "x": "----"})

    def test_fold_td(self):
        td_1_dict = {
                "equal_1": 4, "equal_2": "xyz",
                "concat": "abc",
                "matrix_1": Codes.MATRIX_0, "matrix_2": Codes.STOP,
                "bool_1": Codes.FALSE, "bool_2": Codes.TRUE,
                "yes_no_1": Codes.YES, "yes_no_2": Codes.YES,
                "other_1": "other 1", "other_2": "other 2"
             }

        td_2_dict = {
                "equal_1": 4, "equal_2": "xyz",
                "concat": "def",
                "matrix_1": Codes.MATRIX_1, "matrix_2": Codes.MATRIX_0,
                "bool_1": Codes.TRUE, "bool_2": Codes.TRUE,
                "yes_no_1": Codes.YES, "yes_no_2": Codes.NO,
                "other_1": "other",
            }

        td_1 = TracedData(td_1_dict, Metadata("test_user", Metadata.get_call_location(), 0))
        td_2 = TracedData(td_2_dict, Metadata("test_user", Metadata.get_call_location(), 1))

        folded_td = FoldTracedData.fold_traced_data(
            "test_user", td_1, td_2, equal_keys={"equal_1", "equal_2"}, concat_keys={"concat"},
            matrix_keys={"matrix_1", "matrix_2"}, bool_keys={"bool_1", "bool_2"}, yes_no_keys={"yes_no_1", "yes_no_2"},
            concat_delimiter=". "
        )

        # Test input tds unchanged
        self.assertDictEqual(dict(td_1.items()), td_1_dict)
        self.assertDictEqual(dict(td_2.items()), td_2_dict)

        # Test folded td has expected values
        self.assertDictEqual(
            dict(folded_td.items()),
            {
                "equal_1": 4, "equal_2": "xyz",
                "concat": "abc. def",
                "matrix_1": Codes.MATRIX_1, "matrix_2": Codes.STOP,
                "bool_1": Codes.TRUE, "bool_2": Codes.TRUE,
                "yes_no_1": Codes.YES, "yes_no_2": Codes.BOTH,
                "other_1": "MERGED", "other_2": "MERGED"
            }
        )

        # Test folding only some keys
        folded_td = FoldTracedData.fold_traced_data(
            "test_user", td_1, td_2, matrix_keys={"matrix_1"}, bool_keys={"bool_1", "bool_2"}
        )

        self.assertDictEqual(
            dict(folded_td.items()),
            {
                "equal_1": "MERGED", "equal_2": "MERGED",
                "concat": "MERGED",
                "matrix_1": Codes.MATRIX_1, "matrix_2": "MERGED",
                "bool_1": Codes.TRUE, "bool_2": Codes.TRUE,
                "yes_no_1": "MERGED", "yes_no_2": "MERGED",
                "other_1": "MERGED", "other_2": "MERGED"
            }
        )
