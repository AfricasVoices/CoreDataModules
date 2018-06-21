import unittest

from core_data_modules.cleaners.codes import Codes
from core_data_modules.cleaners.swahili import DemographicCleaner


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

    def test_clean_number_words(self):
        test_cases = {
            "one": 1,
            "eleven": 11,
            "zero": Codes.NotCleaned,
            "sixty-two": 62,
            "seven thirty": 37,  # TODO: Accept unconventional order?
            "six four twenty eight five": 24,  # TODO: Use lowest observed?
            "some text including the number eighty one and some more text": 81,

            "sifuri": Codes.NotCleaned,  # 0
            "ishirini na tatu": 23,
            "kumi na tisa": 19
        }

        self.run_cleaner(DemographicCleaner.clean_number_words, test_cases)

    def test_clean_number_digits(self):
        test_cases = {
            "10": "10",
            "74": "74",
            "09": "09",
            "O2": "02",
            "9": Codes.NotCleaned,  # TODO: Fail to clean single digits?
            "100": Codes.NotCleaned,  # TODO: Fail on long numbers?
            "7 4": Codes.NotCleaned,
            "63 24": "63",  # TODO: Assume first?
            "Text text 14 more text": "14"
        }

        self.run_cleaner(DemographicCleaner.clean_number_digits, test_cases)

    def test_clean_number(self):
        test_cases = {
            "10": "10",
            "27": "27",
            "thirty-four": 34,
            "ishirini na tisa": 29
        }

        self.run_cleaner(DemographicCleaner.clean_number, test_cases)

