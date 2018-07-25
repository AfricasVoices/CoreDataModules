import unittest

from core_data_modules.cleaners.somali import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    def test_clean_somalia_district(self):
        self.assertEqual(DemographicCleaner.clean_somalia_district("I live in Mogadishu"), "mogadishu")
