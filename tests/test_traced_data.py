import collections
import time
import unittest
import six

from core_data_modules.traced_data import TracedData, Metadata


class TestTracedData(unittest.TestCase):
    @staticmethod
    def td_1():
        data = {"id": "0", "phone": "+441632000001", "gender": "man"}
        return TracedData(data, Metadata("test_user", "run_fetcher", time.time()))

    @classmethod
    def td_2(cls, td):
        data_cleaned = {"gender": "male", "age": 30}
        td.append(data_cleaned, Metadata("test_user", "demographic_cleaner", time.time()))

    def test_append(self):
        td = self.td_1()

        self.assertEqual(td.get("id"), "0")
        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("gender"), "man")
        self.assertEqual(td.get("age"), None)
        self.assertEqual(td.get("age", "default"), "default")

        self.td_2(td)

        self.assertEqual(td.get("id"), "0")
        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("gender"), "male")
        self.assertEqual(td.get("age"), 30)

        # TODO: Test that the original data is still available.

    def test___len__(self):
        td = self.td_1()
        self.assertEqual(len(td), 3)

        self.td_2(td)
        self.assertEqual(len(td), 4)

    def test___contains__(self):
        td = self.td_1()

        self.assertEqual("gender" in td, True)
        self.assertEqual("age" in td, False)

        self.assertEqual("gender" not in td, False)
        self.assertEqual("age" not in td, True)

        self.td_2(td)

        self.assertEqual("gender" in td, True)
        self.assertEqual("age" in td, True)

    def test_items(self):
        td = self.td_1()

        # Test that the return type is correct for this version of Python
        if six.PY2:
            self.assertIs(type(td.items()), list)
        if six.PY3:
            self.assertIsInstance(td.items(), collections.ItemsView)

        # Test that the contents of the returned data are the same
        self.assertDictEqual(dict(td.items()),
                             dict([("id", "0"), ("phone", "+441632000001"), ("gender", "man")]))

        self.td_2(td)
        self.assertDictEqual(dict(td.items()),
                             dict([("id", "0"), ("phone", "+441632000001"), ("gender", "male"), ("age", 30)]))

    def test_keys(self):
        td = self.td_1()
        keys = td.keys()

        # Test that the return type is correct for this version of Python
        if six.PY2:
            self.assertIs(type(keys), list)
        if six.PY3:
            self.assertIsInstance(keys, collections.KeysView)

        # Test that the contents of the returned data are the same
        self.assertSetEqual(set(keys), {"id", "phone", "gender"})

        self.td_2(td)

        if six.PY2:
            self.assertSetEqual(set(keys), {"id", "phone", "gender"})
        if six.PY3:
            self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})
            self.assertEqual(len(keys), 4)
            self.assertTrue("phone" in keys)
            self.assertTrue("county" not in keys)

            # Test set operations
            td1 = self.td_1()
            td2 = self.td_1()
            self.td_2(td2)

            self.assertSetEqual(td1.keys() & td2.keys(), {"id", "phone", "gender"})
            self.assertSetEqual(td1.keys() | td2.keys(), {"id", "phone", "gender", "age"})
            self.assertSetEqual(td1.keys() - td2.keys(), set())
            self.assertSetEqual(td2.keys() - td1.keys(), {"age"})
            self.assertSetEqual(td1.keys() ^ td2.keys(), {"age"})

        keys = td.keys()
        self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})

    def test_values(self):
        td = self.td_1()

        # Test that the return type is correct for this version of Python
        if six.PY2:
            self.assertIs(type(td.values()), list)
        if six.PY3:
            self.assertIsInstance(td.values(), collections.ValuesView)

        # Test that the contents of the returned data are the same
        self.assertSetEqual(set(td.values()), {"0", "+441632000001", "man"})

        self.td_2(td)
        self.assertSetEqual(set(td.values()), {"0", "+441632000001", "male", 30})

    def test_iteritems(self):
        td = self.td_1()

        if six.PY3:
            # iteritems was removed in Python 3
            self.assertRaises(AttributeError, lambda: td.iteritems())
            return

        self.assertIsInstance(td.iteritems(), collections.Iterator)
        self.assertDictEqual(dict(td.iteritems()),
                             dict([("id", "0"), ("phone", "+441632000001"), ("gender", "man")]))

        self.td_2(td)
        self.assertDictEqual(dict(td.iteritems()),
                             dict([("id", "0"), ("phone", "+441632000001"), ("gender", "male"), ("age", 30)]))

    def test_iterkeys(self):
        td = self.td_1()

        if six.PY3:
            # iterkeys was removed in Python 3
            self.assertRaises(AttributeError, lambda: td.iterkeys())
            return

        self.assertIsInstance(td.iterkeys(), collections.Iterator)
        self.assertSetEqual(set(td.iterkeys()), {"id", "phone", "gender"})

        self.td_2(td)
        self.assertSetEqual(set(td.iterkeys()), {"id", "phone", "gender", "age"})

    def test_viewkeys(self):
        td = self.td_1()

        if six.PY3:
            # viewkeys was renamed keys in Python 3
            self.assertRaises(AttributeError, lambda: td.viewkeys())
            return

        keys = td.viewkeys()
        self.assertIsInstance(keys, collections.KeysView)
        self.assertSetEqual(set(keys), {"id", "phone", "gender"})

        self.td_2(td)
        self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})
        self.assertEqual(len(keys), 4)
        self.assertTrue("phone" in keys)
        self.assertTrue("county" not in keys)

        keys = td.viewkeys()
        self.assertSetEqual(set(keys), {"id", "phone", "gender", "age"})

        # Test set operations
        td1 = self.td_1()
        td2 = self.td_1()
        self.td_2(td2)

        self.assertSetEqual(td1.viewkeys() & td2.viewkeys(), {"id", "phone", "gender"})
        self.assertSetEqual(td1.viewkeys() | td2.viewkeys(), {"id", "phone", "gender", "age"})
        self.assertSetEqual(td1.viewkeys() - td2.viewkeys(), set())
        self.assertSetEqual(td2.viewkeys() - td1.viewkeys(), {"age"})
        self.assertSetEqual(td1.viewkeys() ^ td2.viewkeys(), {"age"})

    def test_itervalues(self):
        td = self.td_1()

        if six.PY3:
            # itervalues was removed in Python 3
            self.assertRaises(AttributeError, lambda: td.itervalues())
            return

        self.assertIsInstance(td.itervalues(), collections.Iterator)
        self.assertSetEqual(set(td.itervalues()), {"0", "+441632000001", "man"})

        self.td_2(td)
        self.assertSetEqual(set(td.itervalues()), {"0", "+441632000001", "male", 30})

    def test___iter__(self):
        td = self.td_1()
        self.assertIsInstance(iter(td), collections.Iterator)
        self.assertSetEqual(set(iter(td)), {"id", "phone", "gender"})

        self.td_2(td)
        self.assertSetEqual(set(iter(td)), {"id", "phone", "gender", "age"})

    def test___copy__(self):
        # TODO: Figure out how to test this!
        pass
