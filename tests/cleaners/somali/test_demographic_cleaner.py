import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.somali import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    # Note: These are very much place-holders until we work with AVF's annotation team to produce more complete suites.

    def test_clean_genders(self):
        self.assertEqual(DemographicCleaner.clean_gender("woman"), Codes.female)

    def test_clean_yes_no(self):
        self.assertEqual(DemographicCleaner.clean_yes_no("haa"), Codes.yes)
        self.assertEqual(DemographicCleaner.clean_yes_no("mayo"), Codes.no)

    def test_clean_urban_rural(self):
        self.assertEqual(DemographicCleaner.clean_urban_rural("maalo"), Codes.urban)
        self.assertEqual(DemographicCleaner.clean_urban_rural("I am a villager."), Codes.rural)

    def test_clean_somalia_district(self):
        self.assertEqual(DemographicCleaner.clean_somalia_district("I live in Mogadishu"), "mogadishu")

    def test_clean_number_words(self):
        # TODO: This test fails because fifteen matches both 'ten' and 'fifteen', so cleaner is returning 25.
        # self.assertEqual(DemographicCleaner.clean_number_words("fifteen"), 15)

        self.assertEqual(DemographicCleaner.clean_number_words("lix iyo lawatan"), 26)
        self.assertEqual(DemographicCleaner.clean_number_words("I am thirty"), 30)
        self.assertEqual(DemographicCleaner.clean_number_words("one day I will be twenty"), 1 + 20)

    def test_clean_age(self):
        self.assertEqual(DemographicCleaner.clean_age("lix iyo lawatan"), 26)
        self.assertEqual(DemographicCleaner.clean_age("25"), 25)
        self.assertEqual(DemographicCleaner.clean_age("97"), Codes.NotCleaned)
