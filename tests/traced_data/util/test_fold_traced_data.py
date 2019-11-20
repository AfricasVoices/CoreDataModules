import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Label, Origin, CodeScheme, Code
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.util import FoldTracedData
from core_data_modules.traced_data.util.fold_traced_data import FoldStrategies


class TestReconciliationFunctions(unittest.TestCase):
    def test_assert_equal(self):
        self.assertEqual(FoldStrategies.assert_equal("5", "5"), "5")

        try:
            FoldStrategies.assert_equal("6", "7")
            self.fail("No AssertionError raised")
        except AssertionError as e:
            if str(e) == "No AssertionError raised":
                raise e

            self.assertEqual(str(e),
                             "Values should be the same but are different "
                             "(differing values were '6' and '7')")

    def test_control_code(self):
        self.assertEqual(FoldStrategies.control_code(Codes.TRUE_MISSING, Codes.NOT_CODED), Codes.NOT_CODED)
        self.assertEqual(FoldStrategies.control_code(Codes.STOP, Codes.NOT_CODED), Codes.STOP)

    def test_concatenate(self):
        self.assertEqual(FoldStrategies.concatenate("abc", "def"), "abc;def")
        self.assertEqual(FoldStrategies.concatenate("abc", ""), "abc;")
        self.assertEqual(FoldStrategies.concatenate("abc", None), "abc")
        self.assertEqual(FoldStrategies.concatenate("", "def"), ";def")
        self.assertEqual(FoldStrategies.concatenate(None, "def"), "def")
        self.assertEqual(FoldStrategies.concatenate(None, None), None)
        
    def test_boolean_or(self):
        self.assertEqual(FoldStrategies.boolean_or(Codes.TRUE, Codes.TRUE), Codes.TRUE)
        self.assertEqual(FoldStrategies.boolean_or(Codes.FALSE, Codes.TRUE), Codes.TRUE)
        self.assertEqual(FoldStrategies.boolean_or(Codes.FALSE, Codes.FALSE), Codes.FALSE)

    def test_matrix(self):
        self.assertEqual(FoldStrategies.matrix(Codes.MATRIX_1, Codes.MATRIX_1), Codes.MATRIX_1)
        self.assertEqual(FoldStrategies.matrix(Codes.MATRIX_0, Codes.MATRIX_1), Codes.MATRIX_1)
        self.assertEqual(FoldStrategies.matrix(Codes.MATRIX_1, Codes.MATRIX_0), Codes.MATRIX_1)
        self.assertEqual(FoldStrategies.matrix(Codes.MATRIX_0, Codes.MATRIX_0), Codes.MATRIX_0)

    def test_yes_no_amb(self):
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.YES, Codes.YES), Codes.YES)
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.NO, Codes.NO), Codes.NO)
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.YES, Codes.NO), FoldStrategies.AMBIVALENT_BINARY_VALUE)
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.NOT_CODED, Codes.NOT_CODED), Codes.NOT_CODED)

        # TODO: Check that this test case is desired
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.NOT_REVIEWED, Codes.YES), Codes.YES)

    def test_assert_label_ids_equal(self):
        self.assertEqual(FoldStrategies.assert_label_ids_equal(
            Label("scheme-1", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict(),
            Label("scheme-1", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict()
        ), Label("scheme-1", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict())

        self.assertEqual(FoldStrategies.assert_label_ids_equal(
            Label("scheme-1", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict(),
            Label("scheme-1", "code-2", "2019-10-14T12:20:14Z", Origin("y", "test-2", "manual")).to_dict()
        ), Label("scheme-1", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict())

        try:
            FoldStrategies.assert_label_ids_equal(
                Label("scheme-1", "code-1", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict(),
                Label("scheme-1", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict()
            ),
            self.fail("No AssertionError raised")
        except AssertionError as e:
            if str(e) == "No AssertionError raised":
                raise e

            self.assertEqual(str(e),
                             "Labels should have the same SchemeID and CodeID, but at least one of those is different "
                             "(differing values were {'SchemeID': 'scheme-1', 'CodeID': 'code-1'} "
                             "and {'SchemeID': 'scheme-1', 'CodeID': 'code-2'})")

        try:
            FoldStrategies.assert_label_ids_equal(
                Label("scheme-1", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict(),
                Label("scheme-2", "code-2", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict()
            ),
            self.fail("No AssertionError raised")
        except AssertionError as e:
            if str(e) == "No AssertionError raised":
                raise e

            self.assertEqual(str(e),
                             "Labels should have the same SchemeID and CodeID, but at least one of those is different "
                             "(differing values were {'SchemeID': 'scheme-1', 'CodeID': 'code-2'} "
                             "and {'SchemeID': 'scheme-2', 'CodeID': 'code-2'})")

    def test_fold_list_of_labels(self):
        na_code = Code("code-NA", "Control", "NA", -10, "NA", True, control_code=Codes.TRUE_MISSING)
        nr_code = Code("code-NR", "Control", "NR", -10, "NA", True, control_code=Codes.NOT_REVIEWED)
        normal_1_code = Code("code-normal-1", "Normal", "Normal 1", 1, "normal_1", True)
        normal_2_code = Code("code-normal-2", "Normal", "Normal 2", 2, "normal_2", True)
        scheme_1 = CodeScheme("scheme-1", "Scheme 1", "1", [na_code, nr_code, normal_1_code, normal_2_code])

        scheme_2 = CodeScheme("scheme-2", "Scheme 2", "2", [])

        na_label = Label("scheme-1", "code-NA", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict()
        nr_label = Label("scheme-1", "code-NR", "2019-10-01T12:25:18Z", Origin("x", "test", "automatic")).to_dict()
        na_label_2 = Label("scheme-1", "code-NA", "2019-10-01T13:00:00Z", Origin("x", "test", "automatic")).to_dict()
        normal_1_label = Label("scheme-1", "code-normal-1", "2019-10-01T12:20:14Z", Origin("x", "test", "automatic")).to_dict()
        normal_1_label_2 = Label("scheme-1", "code-normal-1", "2019-10-03T00:00:00Z", Origin("x", "test", "automatic")).to_dict()
        normal_2_label = Label("scheme-1", "code-normal-2", "2019-10-01T15:00:00Z", Origin("x", "test", "automatic")).to_dict()

        # Test empty lists are rejected
        self.assertRaises(AssertionError, lambda: FoldStrategies.list_of_labels(scheme_1, [], []))
        self.assertRaises(AssertionError, lambda: FoldStrategies.list_of_labels(scheme_1, [na_label], []))

        # Test lists containing only NA labels return a single NA label
        self.assertEqual(FoldStrategies.list_of_labels(scheme_1, [na_label], [na_label]), [na_label])
        self.assertEqual(FoldStrategies.list_of_labels(scheme_1, [na_label], [na_label_2]), [na_label])

        # Test lists containing an NA label and another label (including another NA label) are rejected
        self.assertRaises(AssertionError, lambda: FoldStrategies.list_of_labels(scheme_1, [na_label, na_label], [na_label]))
        self.assertRaises(AssertionError, lambda: FoldStrategies.list_of_labels(scheme_1, [na_label, normal_1_label], [na_label]))

        # Test folding a normal label with an NA label
        self.assertEqual(FoldStrategies.list_of_labels(scheme_1, [na_label], [normal_1_label]), [normal_1_label])
        
        # Test folding various combinations of only normal labels
        self.assertEqual(FoldStrategies.list_of_labels(scheme_1, [normal_1_label], [normal_1_label]), [normal_1_label])
        self.assertEqual(FoldStrategies.list_of_labels(scheme_1, [normal_1_label, normal_2_label], [normal_1_label]),
                         [normal_1_label, normal_2_label])
        self.assertEqual(FoldStrategies.list_of_labels(scheme_1, [normal_1_label, normal_2_label], [normal_1_label_2]),
                         [normal_1_label, normal_2_label])

        # Test folding normal labels with a control code that isn't NA or NC
        self.assertEqual(FoldStrategies.list_of_labels(scheme_1, [normal_1_label, normal_2_label], [nr_label]),
                         [normal_1_label, normal_2_label, nr_label])

        # Test folding a label from a different code scheme
        self.assertRaises(AssertionError, lambda: FoldStrategies.list_of_labels(scheme_2, [normal_1_label], [na_label]))
        # (make sure that test would have been ok with the correct code scheme)
        FoldStrategies.list_of_labels(scheme_1, [normal_1_label], [na_label])

        # TODO: Test folding normal codes with NC codes


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

    def test_fold_traced_data(self):
        td_1_dict = {
                "equal_1": 4, "equal_2": "xyz",
                "concat": "abc",
                "matrix_1": Codes.MATRIX_0, "matrix_2": Codes.MATRIX_0,
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

        fold_strategies = {
            "equal_1": FoldStrategies.assert_equal,
            "equal_2": FoldStrategies.assert_equal,
            "concat": FoldStrategies.concatenate,
            "bool_1": FoldStrategies.boolean_or,
            "bool_2": FoldStrategies.boolean_or,
            "matrix_1": FoldStrategies.matrix,
            "matrix_2": FoldStrategies.matrix,
            "yes_no_1": FoldStrategies.yes_no_amb,
            "yes_no_2": FoldStrategies.yes_no_amb
        }
        folded_td = FoldTracedData.fold_traced_data("test_user", td_1, td_2, fold_strategies)

        # Test input tds unchanged
        self.assertDictEqual(dict(td_1.items()), td_1_dict)
        self.assertDictEqual(dict(td_2.items()), td_2_dict)
        
        # Test folded td has expected values
        self.assertDictEqual(
            dict(folded_td.items()),
            {
                "equal_1": 4, "equal_2": "xyz",
                "concat": "abc;def",
                "matrix_1": Codes.MATRIX_1, "matrix_2": Codes.MATRIX_0,
                "bool_1": Codes.TRUE, "bool_2": Codes.TRUE,
                "yes_no_1": Codes.YES, "yes_no_2": FoldStrategies.AMBIVALENT_BINARY_VALUE,
            }
        )
