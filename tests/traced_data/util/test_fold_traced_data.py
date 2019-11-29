import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.util import FoldTracedData
from core_data_modules.traced_data.util.fold_traced_data import FoldStrategies


class TestReconciliationFunctions(unittest.TestCase):
    def test_assert_equal(self):
        # This test is considered successful if no assertion is raised
        FoldStrategies.assert_equal("5", "5")

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
        self.assertEqual(FoldStrategies.control_code_by_precedence(Codes.TRUE_MISSING, Codes.NOT_CODED), Codes.NOT_CODED)
        self.assertEqual(FoldStrategies.control_code_by_precedence(Codes.STOP, Codes.NOT_CODED), Codes.STOP)

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
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.YES, Codes.NO), Codes.AMBIVALENT)
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.NOT_CODED, Codes.NOT_CODED), Codes.NOT_CODED)

        # TODO: Check that this test case is desired
        self.assertEqual(FoldStrategies.yes_no_amb(Codes.NOT_REVIEWED, Codes.YES), Codes.YES)


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
                "yes_no_1": Codes.YES, "yes_no_2": Codes.AMBIVALENT
            }
        )
