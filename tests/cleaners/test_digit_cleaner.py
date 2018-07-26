import unittest

from core_data_modules.cleaners import DigitCleaner, Codes


class TestDigitCleaner(unittest.TestCase):
    def run_cleaner_tests(self, cleaner, test_cases):
        for raw, expected in test_cases.items():
            clean = cleaner(raw)
            self.assertEqual(clean, expected)

    def test_replace_digit_like_characters(self):
        test_cases = {
            "o": "0",
            " ijzt": " 1127",
            "o1 z3": "01 23",
            "O": "0",
            "HeLLO": "He110"
        }

        self.run_cleaner_tests(DigitCleaner.replace_digit_like_characters, test_cases)

    def test_clean_number_digits(self):
        test_cases = {
            "10": "10",
            "74": "74",
            "09": "09",
            "O2": "02",
            "9": Codes.NotCoded,  # TODO: Fail to clean single digits?
            "100": Codes.NotCoded,  # TODO: Fail on long numbers?
            "7 4": Codes.NotCoded,
            "63 24": "63",  # TODO: Assume first?
            "Text text 14 more text": "14"
        }

        self.run_cleaner_tests(DigitCleaner.clean_number_digits, test_cases)
