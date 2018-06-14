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

    def test_fold_lines(self):
        test_cases = {
            "": "",
            "a": "a",
            "line 1\nline 2": "line 1 line 2"
        }

        for raw, expected in test_cases.items():
            clean = TextCleaner.fold_lines(raw)
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
