# coding=utf-8
import unittest

from core_data_modules.cleaners import TextCleaner


class TestTextCleaner(unittest.TestCase):
    def test_remove_non_ascii(self):
        test_cases = {
            "abc": "abc",
            "!": "!",
            u"Ø": "",
            u"tøåst": "tst",
            "ABC def": "ABC def",
            u"abc, å dEf": "abc,  dEf"
        }

        for raw, expected in test_cases.items():
            clean = TextCleaner.to_ascii(raw)
            self.assertEqual(expected, clean)

    def test_clean_text(self):
        test_cases = {
            "abc": "abc",
            "!": " ",
            u"ø": "",
            u"tøåst": "tst",
            "ABC def": "abc def",
            u"abc, å dEf": "abc   def"
        }

        for raw, expected in test_cases.items():
            clean = TextCleaner.clean_text(raw)
            self.assertEqual(expected, clean)
