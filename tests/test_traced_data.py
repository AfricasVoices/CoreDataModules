import collections
import time
import unittest
import six

from core_data_modules.traced_data import TracedData, Metadata


class TestTracedData(unittest.TestCase):
    @staticmethod
    def generate_test_data():
        data = {"id": "0", "phone": "+441632000001", "gender": "man"}
        return TracedData(data, Metadata("test_user", "run_fetcher", time.time()))

    @classmethod
    def append_test_data(cls, td):
        data_cleaned = {"gender": "male", "age": 30}
        td.append(data_cleaned, Metadata("test_user", "demographic_cleaner", time.time()))

    def test_append(self):
        td = self.generate_test_data()

        self.assertEqual(td.get("id"), "0")
        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("gender"), "man")
        self.assertEqual(td["gender"], "man")
        self.assertEqual(td.get("age"), None)
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
