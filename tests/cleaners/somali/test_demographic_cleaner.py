import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.somali import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    # Note: These are very much place-holders until we work with AVF's annotation team to produce more complete suites.

    def test_clean_genders(self):
        self.assertEqual(DemographicCleaner.clean_gender("woman"), Codes.FEMALE)

    def test_clean_yes_no(self):
        self.assertEqual(DemographicCleaner.clean_yes_no("haa"), Codes.YES)
        self.assertEqual(DemographicCleaner.clean_yes_no("mayo"), Codes.NO)

    def test_clean_urban_rural(self):
        self.assertEqual(DemographicCleaner.clean_urban_rural("maalo"), Codes.URBAN)
        self.assertEqual(DemographicCleaner.clean_urban_rural("I am a villager."), Codes.RURAL)

    def test_clean_somalia_district(self):
        self.assertEqual(DemographicCleaner.clean_somalia_district("I live in Mogadishu"), "mogadishu")
