import collections
import time
import unittest

import six

from core_data_modules.traced_data import TracedData, Metadata


class TestMetadata(unittest.TestCase):
    def test_get_call_location(self):
        call_location = Metadata.get_call_location()
        # call_location contains an absolute path, but this only tests the end of that path so that it can run
        # independently of the project's location.
        self.assertTrue(call_location.endswith("tests/traced_data/test_traced_data.py:12:test_get_call_location"))


class TestTracedData(unittest.TestCase):
    @staticmethod
    def generate_test_data():
        """Returns a new TracedData object with example id, phone, and gender fields"""
        data = {"id": "0", "phone": "+441632000001", "gender": "man"}
        return TracedData(data, Metadata("test_user", "run_fetcher", time.time()))

    @classmethod
    def append_test_data(cls, td):
        """Updates the gender field and adds an age field to the given TracedData object (td)"""
        data_cleaned = {"gender": "male", "age": 30}
        td.append_data(data_cleaned, Metadata("test_user", "demographic_cleaner", time.time()))

    def test_append_data(self):
        td = self.generate_test_data()

        self.assertEqual(td.get("id"), "0")
        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("gender"), "man")
        self.assertEqual(td["gender"], "man")
        self.assertEqual(td.get("age"), None)
        self.assertRaises(KeyError, lambda: td["age"])
        self.assertEqual(td.get("age", "default"), "default")

        self.append_test_data(td)

        self.assertEqual(td.get("id"), "0")
        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("gender"), "male")
        self.assertEqual(td["gender"], "male")
        self.assertEqual(td.get("age"), 30)

        # Test that the original data is still available.
        history = td.get_history("gender")
        self.assertListEqual(list(map(lambda x: x["value"], history)), ["man", "male"])

    def test__sha_with_prev(self):
        self.assertEqual(
            TracedData._sha_with_prev(
                {"phone": "+441632000001", "age": 20},
                "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
            ),
            "7e7f3e31168dd8587dac8a58858b17d7644c21400b91ae000f3fcb0f6f8017d4"
        )

        self.assertEqual(
            TracedData._sha_with_prev({"phone": "+441632000001", "age": 20}, None),
            "5e106f6389b42724efb754067be30d67473ce7f443464c565a8e4d57e62d1fd3"
        )

    def test___len__(self):
        td = self.generate_test_data()
        self.assertEqual(len(td), 3)

        self.append_test_data(td)
        self.assertEqual(len(td), 4)

    def test___contains__(self):
        td = self.generate_test_data()

        self.assertTrue("gender" in td)
        self.assertFalse("age" in td)

        self.assertFalse("gender" not in td)
        self.assertTrue("age" not in td)

        self.append_test_data(td)

        self.assertTrue("gender" in td)
        self.assertTrue("age" in td)

    def test___iter__(self):
        td = self.generate_test_data()
        self.assertIsInstance(iter(td), collections.Iterator)
        self.assertSetEqual(set(iter(td)), {"id", "phone", "gender"})

        self.append_test_data(td)
        self.assertSetEqual(set(iter(td)), {"id", "phone", "gender", "age"})

    if six.PY2:
        def test_has_key(self):
            td = self.generate_test_data()
            self.assertTrue(td.has_key("gender"))
            self.assertFalse(td.has_key("age"))

            self.append_test_data(td)
            self.assertTrue(td.has_key("age"))

        def test_keys(self):
            td = self.generate_test_data()

            keys = td.keys()
            self.assertIs(type(keys), list)
            self.assertSetEqual(set(keys), {"id", "phone", "gender"})

            self.append_test_data(td)
            self.assertSetEqual(set(keys), {"id", "phone", "gender"})

            keys = td.keys()
            self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})

        def test_values(self):
            td = self.generate_test_data()

            values = td.values()
            self.assertIs(type(values), list)
            self.assertSetEqual(set(values), {"0", "+441632000001", "man"})

            self.append_test_data(td)
            self.assertSetEqual(set(values), {"0", "+441632000001", "man"})

            values = td.values()
            self.assertSetEqual(set(values), {"0", "+441632000001", "male", 30})

        def test_items(self):
            td = self.generate_test_data()

            items = td.items()
            self.assertIs(type(items), list)
            self.assertDictEqual(dict(td.items()),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "man")]))

            self.append_test_data(td)
            self.assertDictEqual(dict(items),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "man")]))

        def test_iterkeys(self):
            td = self.generate_test_data()

            self.assertIsInstance(td.iterkeys(), collections.Iterator)
            self.assertSetEqual(set(td.iterkeys()), {"id", "phone", "gender"})

            self.append_test_data(td)
            self.assertSetEqual(set(td.iterkeys()), {"id", "phone", "gender", "age"})

        def test_itervalues(self):
            td = self.generate_test_data()

            self.assertIsInstance(td.itervalues(), collections.Iterator)
            self.assertSetEqual(set(td.itervalues()), {"0", "+441632000001", "man"})

            self.append_test_data(td)
            self.assertSetEqual(set(td.itervalues()), {"0", "+441632000001", "male", 30})

        def test_iteritems(self):
            td = self.generate_test_data()

            self.assertIsInstance(td.iteritems(), collections.Iterator)
            self.assertDictEqual(dict(td.iteritems()),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "man")]))

            self.append_test_data(td)
            self.assertDictEqual(dict(td.iteritems()),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "male"), ("age", 30)]))

        def test_viewkeys(self):
            td = self.generate_test_data()

            keys = td.viewkeys()
            self.assertIsInstance(keys, collections.KeysView)
            self.assertSetEqual(set(keys), {"id", "phone", "gender"})

            self.append_test_data(td)
            self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})
            self.assertEqual(len(keys), 4)
            self.assertTrue("phone" in keys)
            self.assertTrue("county" not in keys)

            keys = td.viewkeys()
            self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})

            # Test set operations
            td1 = self.generate_test_data()
            td2 = self.generate_test_data()
            self.append_test_data(td2)
            self.viewkeys_set_like_helper(td1.viewkeys(), td2.viewkeys())

        def test_viewvalues(self):
            td = self.generate_test_data()

            values = td.viewvalues()
            self.assertIsInstance(values, collections.ValuesView)
            self.assertSetEqual(set(values), {"0", "+441632000001", "man"})

            self.append_test_data(td)
            self.assertSetEqual(set(values), {"0", "+441632000001", "male", 30})
            self.assertEqual(len(values), 4)
            self.assertTrue(30 in values)
            self.assertTrue("female" not in values)

            values = td.viewvalues()
            self.assertSetEqual(set(values), {"0", "+441632000001", "male", 30})

        def test_viewitems(self):
            td = self.generate_test_data()

            items = td.viewitems()
            self.assertIsInstance(items, collections.ItemsView)
            self.assertDictEqual(dict(items),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "man")]))

            self.append_test_data(td)
            self.assertDictEqual(dict(items),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "male"), ("age", 30)]))
            self.assertEqual(len(items), 4)
            self.assertTrue(("id", "0") in items)
            self.assertTrue(("id", "1") not in items)

            items = td.viewitems()
            self.assertDictEqual(dict(items),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "male"), ("age", 30)]))

            # Test set operations
            td1 = self.generate_test_data()
            td2 = self.generate_test_data()
            self.append_test_data(td2)
            self.viewitems_set_like_helper(td1.viewitems(), td2.viewitems())

    if six.PY3:
        def test_keys(self):
            td = self.generate_test_data()

            keys = td.keys()
            self.assertIsInstance(keys, collections.KeysView)

            # Test that the contents of the returned data are the same
            self.assertSetEqual(set(keys), {"id", "phone", "gender"})

            self.append_test_data(td)
            self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})
            self.assertEqual(len(keys), 4)
            self.assertTrue("phone" in keys)
            self.assertTrue("county" not in keys)

            # Test set operations
            td1 = self.generate_test_data()
            td2 = self.generate_test_data()
            self.append_test_data(td2)
            self.viewkeys_set_like_helper(td1.keys(), td2.keys())

            keys = td.keys()
            self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})

        def test_values(self):
            td = self.generate_test_data()

            values = td.values()
            self.assertIsInstance(values, collections.ValuesView)

            # Test that the contents of the returned data are the same
            self.assertSetEqual(set(values), {"0", "+441632000001", "man"})

            self.append_test_data(td)
            self.assertSetEqual(set(values), {"0", "+441632000001", "male", 30})
            self.assertEqual(len(values), 4)
            self.assertTrue(30 in values)
            self.assertTrue("female" not in values)

            values = td.values()
            self.assertSetEqual(set(values), {"0", "+441632000001", "male", 30})

        def test_items(self):
            td = self.generate_test_data()

            items = td.items()
            self.assertIsInstance(items, collections.ItemsView)
            self.assertDictEqual(dict(td.items()),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "man")]))

            self.append_test_data(td)
            self.assertDictEqual(dict(items),
                                 dict([("id", "0"), ("phone", "+441632000001"), ("gender", "male"), ("age", 30)]))
            self.assertEqual(len(items), 4)
            self.assertTrue(("id", "0") in items)
            self.assertTrue(("id", "1") not in items)

            td1 = self.generate_test_data()
            td2 = self.generate_test_data()
            self.append_test_data(td2)
            self.viewitems_set_like_helper(td1.items(), td2.items())

        def test_no_PY2_methods(self):
            td = self.generate_test_data()

            self.assertRaises(AttributeError, lambda: td.iterkeys())
            self.assertRaises(AttributeError, lambda: td.itervalues())
            self.assertRaises(AttributeError, lambda: td.iteritems())

            self.assertRaises(AttributeError, lambda: td.viewkeys())
            self.assertRaises(AttributeError, lambda: td.viewvalues())
            self.assertRaises(AttributeError, lambda: td.iteritems())

    def viewitems_set_like_helper(self, a, b):
        self.assertSetEqual(a & b,
                            {("id", "0"), ("phone", "+441632000001")})
        self.assertSetEqual(a | b,
                            {("id", "0"), ("phone", "+441632000001"), ("gender", "man"), ("gender", "male"),
                             ("age", 30)})
        self.assertSetEqual(a - b, {("gender", "man")})
        self.assertSetEqual(b - a, {("gender", "male"), ("age", 30)})
        self.assertSetEqual(a ^ b, {("gender", "man"), ("gender", "male"), ("age", 30)})

    def viewkeys_set_like_helper(self, a, b):
        self.assertSetEqual(a & b, {"id", "phone", "gender"})
        self.assertSetEqual(a | b, {"id", "phone", "gender", "age"})
        self.assertSetEqual(a - b, set())
        self.assertSetEqual(b - a, {"age"})
        self.assertSetEqual(a ^ b, {"age"})

    def test_copy(self):
        td = self.generate_test_data()
        self.append_test_data(td)
        td_copy = td.copy()

        self.assertFalse(td is td_copy)
        self.assertTrue(td == td_copy)

    def test_join_iterables(self):
        data_1 = [
            TracedData(
                {"id": "A", "gender": "male", "age": 55},
                Metadata("test_user", Metadata.get_call_location(), time.time())
            ),
            TracedData(
                {"id": "B", "age": 19},
                Metadata("test_user", Metadata.get_call_location(), time.time())
            )
        ]

        data_2 = [
            TracedData(
                {"id": "C", "country": "Somalia"},
                Metadata("test_user", Metadata.get_call_location(), time.time())
            ),
            TracedData(
                {"id": "A", "country": "Kenya", "gender": "female"},
                Metadata("test_user", Metadata.get_call_location(), time.time())
            )
        ]

        # Joining should file because item with id 'A' has conflicting genders
        self.assertRaises(AssertionError, lambda: TracedData.join_iterables("test_user", "id", data_1, data_2, "data_2"))

        # Fix the gender conflict problem, and test that the join now works as expected.
        data_2[1].append_data({"gender": "male"}, Metadata("test_user", Metadata.get_call_location(), time.time()))
        merged = TracedData.join_iterables("test_user", "id", data_1, data_2, "data_2")

        merged_dicts = [dict(td.items()) for td in merged]
        expected_dicts = [
            {"id": "B", "age": 19},
            {"id": "C", "country": "Somalia"},
            {"id": "A", "gender": "male", "age": 55, "country": "Kenya"}
        ]
        
        self.assertEquals(len(merged_dicts), len(expected_dicts))

        for merged, expected in zip(merged_dicts, expected_dicts):
            self.assertDictEqual(merged, expected)

        # Modify data_1 to include multiple TracedData objects with the same join key, and ensure joining then fails.
        data_1[0].append_data({"id": "B"}, Metadata("test_user", Metadata.get_call_location(), time.time()))
        self.assertRaises(AssertionError, lambda: TracedData.join_iterables("test_user", "id", data_1, data_2, "data_2"))

    def test_update_iterable(self):
        data_dicts = [
            {"id": "A", "message": "hello"},
            {"id": "B", "message": "hello"},
            {"id": "A", "message": "hi"}
        ]
        data = [
            TracedData(d, Metadata("test_user", "data_generator", time.time()))
            for d in data_dicts
        ]

        updates_dicts = [
            {"id": "A", "gender": "male"},
            {"id": "B", "gender": "female", "age": 20}
        ]
        updates = [
            TracedData(d, Metadata("test_user", "data_generator", time.time()))
            for d in updates_dicts
        ]

        TracedData.update_iterable("test_user", "id", data, updates, "demographics")

        expected_dicts = [
            {"id": "A", "message": "hello", "gender": "male"},
            {"id": "B", "message": "hello", "gender": "female", "age": 20},
            {"id": "A", "message": "hi", "gender": "male"}
        ]

        for td, expected_dict in zip(data, expected_dicts):
            self.assertDictEqual(dict(td.items()), expected_dict)


class TestTracedDataAppendTracedData(unittest.TestCase):
    """
    Test cases for TracedData which has had another set of traced data appended.
    """

    @staticmethod
    def generate_message_td():
        message_data = {"phone": "+441632000001", "message": "Hello AVF!"}
        message_td = TracedData(message_data, Metadata("test_user", "run_fetcher", time.time()))
        message_td.append_data({"message": "hello avf"}, Metadata("test_user", "message_cleaner", time.time()))

        return message_td

    @staticmethod
    def generate_demog_1_td():
        demog_1_data = {"phone": "+441632000001", "gender": "woman", "age": "twenty"}
        demog_1_td = TracedData(demog_1_data, Metadata("test_user", "run_fetcher", time.time()))
        demog_1_td.append_data({"gender": "female", "age": 20}, Metadata("test_user", "demog_cleaner", time.time()))

        return demog_1_td

    @staticmethod
    def generate_demog_2_td():
        demog_2_data = {"phone": "+441632000001", "country": "Kenyan citizen"}
        demog_2_td = TracedData(demog_2_data, Metadata("test_user", "run_fetcher", time.time()))
        demog_2_td.append_data({"country": "Kenya"}, Metadata("test_user", "demog_cleaner", time.time()))

        return demog_2_td

    @classmethod
    def generate_test_data(cls):
        """Returns a new TracedData object with example id, phone, and gender fields"""
        message_td = cls.generate_message_td()

        demog_1_td = cls.generate_demog_1_td()
        demog_2_td = cls.generate_demog_2_td()

        message_td.append_traced_data("demog_1", demog_1_td, Metadata("test_user", "demog_1_append", time.time()))
        message_td.append_traced_data("demog_2", demog_2_td, Metadata("test_user", "demog_2_append", time.time()))

        return message_td

    def test_append_traced_data(self):
        # Note that this only tests failing appends. Successful appends are tested by the other methods in this suite.
        message_td = self.generate_message_td()

        demog_1_td = self.generate_demog_1_td()
        demog_1_td.append_data({"message": "should-fail"}, Metadata("test_user", "conflicting_message", time.time()))

        self.assertRaises(AssertionError,
                          lambda: message_td.append_traced_data(
                              "demog_1", demog_1_td, Metadata("test_user", "demog_1_append", time.time())))

    def test__traced_repr(self):
        demog_1_td = self.generate_demog_1_td()

        self.assertDictEqual(
            TracedData._replace_traced_with_sha({"phone": "+441632000001", "demog_1": demog_1_td}),
            {"phone": "+441632000001", "demog_1": demog_1_td._sha}
        )

    def test___get_item__(self):
        td = self.generate_test_data()

        self.assertEqual(td["phone"], "+441632000001")
        self.assertEqual(td["message"], "hello avf")
        self.assertEqual(td["age"], 20)
        self.assertEqual(td["country"], "Kenya")

        self.assertRaises(KeyError, lambda: td["education"])

    def test_get(self):
        td = self.generate_test_data()

        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("message"), "hello avf")
        self.assertEqual(td.get("age"), 20)
        self.assertEqual(td.get("country"), "Kenya")

        self.assertEqual(td.get("education"), None)
        self.assertEqual(td.get("education", "default"), "default")

    def test___len__(self):
        td = self.generate_test_data()

        self.assertEqual(len(td), 5)

    def test___contains__(self):
        td = self.generate_test_data()

        self.assertTrue("phone" in td)
        self.assertTrue("message" in td)
        self.assertTrue("country" in td)
        self.assertFalse("education" in td)

        # Test that appended TracedData objects are still available
        self.assertTrue("demog_1" in td)
        self.assertTrue("demog_2" in td)

        self.assertFalse("country" not in td)
        self.assertTrue("education" not in td)

    def test___iter__(self):
        td = self.generate_test_data()

        self.assertSetEqual(
            set(iter(td)),  # Relying on tests in TestTracedData for type checks
            {"phone", "message", "gender", "age", "country"}
        )

    def test_keys(self):
        td = self.generate_test_data()

        self.assertSetEqual(
            set(td.keys()),  # Relying on tests in TestTracedData for type checks
            {"phone", "message", "gender", "age", "country"}
        )

    def test_values(self):
        td = self.generate_test_data()

        self.assertSetEqual(
            set(td.values()),  # Relying on tests in TestTracedData for type checks
            {"+441632000001", "Kenya", "hello avf", "female", 20}
        )

    def test_items(self):
        td = self.generate_test_data()

        self.assertDictEqual(
            dict(td.items()),  # Relying on tests in TestTracedData for type checks
            {"phone": "+441632000001", "country": "Kenya", "message": "hello avf",
             "gender": "female", "age": 20}
        )

    if six.PY2:
        def test_has_key(self):
            td = self.generate_test_data()

            self.assertTrue(td.has_key("phone"))
            self.assertTrue(td.has_key("country"))
            self.assertFalse(td.has_key("education"))

    def test_copy(self):
        td = self.generate_test_data()
        td_copy = td.copy()

        self.assertFalse(td is td_copy)
        self.assertTrue(td == td_copy)

    def test_get_history(self):
        td = self.generate_test_data()

        history = td.get_history("gender")
        self.assertListEqual(list(map(lambda x: x["value"], history)), ["woman", "female"])

        # Test diverging histories
        td = self.generate_demog_1_td()

        td_2 = self.generate_demog_2_td()
        td_2.append_data({"gender": "girl"}, Metadata("test_user", "gender_input", time.time()))
        td_2.append_data({"gender": "female"}, Metadata("test_user", "gender_cleaner", time.time()))

        td.append_traced_data("demog_2", td_2, Metadata("test_user", "demog_2_append", time.time()))

        history = td.get_history("gender")
        self.assertEqual(list(map(lambda x: x["value"], history)), ["woman", "female", "girl", "female"])

