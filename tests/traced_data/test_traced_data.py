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
        self.assertRaises(AssertionError, lambda: TracedData.join_iterables("test_user", "id", data_1, data_2))

        # Fix the gender conflict problem, and test that the join now works as expected.
        data_2[1].append_data({"gender": "male"}, Metadata("test_user", Metadata.get_call_location(), time.time()))
        merged = TracedData.join_iterables("test_user", "id", data_1, data_2)

        merged_dicts = map(lambda td: dict(td.items()), merged)
        expected_dicts = [
            {"id": "B", "age": 19},
            {"id": "C", "country": "Somalia"},
            {"id": "A", "gender": "male", "age": 55, "country": "Kenya"}
        ]

        for merged, expected in zip(merged_dicts, expected_dicts):
            self.assertDictEqual(merged, expected)

        # Modify data_1 to include multiple TracedData objects with the same join key, and ensure joining then fails.
        data_1[0].append_data({"id": "B"}, Metadata("test_user", Metadata.get_call_location(), time.time()))
        self.assertRaises(AssertionError, lambda: TracedData.join_iterables("test_user", "id", data_1, data_2))
