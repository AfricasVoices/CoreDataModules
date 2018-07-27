import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.swahili import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    def run_cleaner_tests(self, cleaner, test_cases):
        for raw, expected in test_cases.items():
            clean = cleaner(raw)
            self.assertEqual(clean, expected)

    def test_clean_gender(self):
        test_cases = {
            "kiume": Codes.MALE,
            "female": Codes.FEMALE,
            "  KiUme": Codes.MALE
        }

        self.run_cleaner_tests(DemographicCleaner.clean_gender, test_cases)

    def test_clean_number_words(self):
        test_cases = {
            "one": 1,
            "eleven": 11,
            "zero": Codes.NOT_CODED,
            "sixty-two": 62,
            "seven thirty": 37,  # TODO: Accept unconventional order?
            "six four twenty eight five": 24,  # TODO: Use lowest observed?
            "some text including the number eighty one and some more text": 81,

            "sifuri": Codes.NOT_CODED,  # 0
            "ishirini na tatu": 23,
            "kumi na tisa": 19
        }

        self.run_cleaner_tests(DemographicCleaner.clean_number_words, test_cases)

    def test_clean_number(self):
        test_cases = {
            "10": 10,
            "27": 27,
            "thirty-four": 34,
            "ishirini na tisa": 29
        }

        self.run_cleaner_tests(DemographicCleaner.clean_number, test_cases)

