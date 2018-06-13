import unittest

from core_data_modules.cleaners.codes import Codes
from core_data_modules.cleaners.swahili.demographic_cleaner import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    def run_cleaner(self, cleaner, test_cases):
        for raw, expected in test_cases.items():
            clean = cleaner(raw)
            self.assertEqual(clean, expected)

    def test_clean_gender(self):
        test_cases = {
            "kiume": Codes.male,
            "female": Codes.female,
            "  KiUme": Codes.male
        }

        self.run_cleaner(DemographicCleaner.clean_gender, test_cases)

    def test_replace_digit_like_characters(self):
        test_cases = {
            "o": "0",
            " ijzt": " 1127",
            "o1 z3": "01 23",
            "O": "0",
            "HeLLO": "He110"
        }

        self.run_cleaner(DemographicCleaner.replace_digit_like_characters, test_cases)

    def test_clean_number_digits(self):
        test_cases = {
            "10": "10",
            "74": "74",
            "09": "09",  # TODO: Keep leading 0?
            "9": Codes.NotCleaned,  # TODO: Fail to clean single digits?
            "100": Codes.NotCleaned,
            "7 4": Codes.NotCleaned,
            "63 24": "63"  # TODO: Assume first?
        }

        self.run_cleaner(DemographicCleaner.clean_number_digits, test_cases)

    def test_clean_number(self):
        test_cases = {
            "10": "10",
            "27": "27"
        }

        self.run_cleaner(DemographicCleaner.clean_number, test_cases)

