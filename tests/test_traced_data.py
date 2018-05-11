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
    def td_2(cls):
        td = cls.td_1()
        data_cleaned = {"gender": "male", "age": 30}
        td.append(data_cleaned, Metadata("test_user", "demographic_cleaner", time.time()))
        return td

    def test_append(self):
        td = self.td_1()

        self.assertEqual(td.get("id"), "0")
        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("gender"), "man")
        self.assertEqual(td.get("age"), None)
        self.assertEqual(td.get("age", "default"), "default")

        td = self.td_2()

        self.assertEqual(td.get("id"), "0")
        self.assertEqual(td.get("phone"), "+441632000001")
        self.assertEqual(td.get("gender"), "male")
        self.assertEqual(td.get("age"), 30)

        # TODO: Test that the original data is still available.

    def test___contains__(self):
        td = self.td_1()

        self.assertEqual("gender" in td, True)
        self.assertEqual("age" in td, False)

        self.assertEqual("gender" not in td, False)
        self.assertEqual("age" not in td, True)

        td = self.td_2()

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

        td = self.td_2()
        self.assertDictEqual(dict(td.items()),
                             dict([("id", "0"), ("phone", "+441632000001"), ("gender", "male"), ("age", 30)]))

    def test_keys(self):
        td = self.td_1()

        # Test that the return type is correct for this version of Python
        if six.PY2:
            self.assertIs(type(td.keys()), list)
        if six.PY3:
            self.assertIsInstance(td.keys(), collections.KeysView)

        # Test that the contents of the returned data are the same
        self.assertSetEqual(set(td.keys()), {"id", "phone", "gender"})

        td = self.td_2()
        self.assertSetEqual(set(td.keys()), {"id", "phone", "gender", "age"})

    def test_values(self):
        td = self.td_1()

        # Test that the return type is correct for this version of Python
        if six.PY2:
            self.assertIs(type(td.values()), list)
        if six.PY3:
            self.assertIsInstance(td.values(), collections.ValuesView)

        # Test that the contents of the returned data are the same
        self.assertSetEqual(set(td.values()), {"0", "+441632000001", "man"})

        td = self.td_2()
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

        td = self.td_2()
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

        td = self.td_2()
        self.assertSetEqual(set(td.iterkeys()), {"id", "phone", "gender", "age"})

    def test_itervalues(self):
        td = self.td_1()

        if six.PY3:
            # itervalues was removed in Python 3
            self.assertRaises(AttributeError, lambda: td.itervalues())
            return

        self.assertIsInstance(td.itervalues(), collections.Iterator)
        self.assertSetEqual(set(td.itervalues()), {"0", "+441632000001", "man"})

        td = self.td_2()
        self.assertSetEqual(set(td.itervalues()), {"0", "+441632000001", "male", 30})

    def test_iter(self):
        td = self.td_1()
        self.assertIsInstance(iter(td), collections.Iterator)
        self.assertSetEqual(set(iter(td)), {"id", "phone", "gender"})

        td = self.td_2()
        self.assertSetEqual(set(iter(td)), {"id", "phone", "gender", "age"})
