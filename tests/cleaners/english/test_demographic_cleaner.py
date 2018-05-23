import unittest

from core_data_modules.cleaners.english.demographic_cleaner import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    def test_clean_gender(self):
        self.assertEqual(DemographicCleaner.clean_gender("m"), "M")
        self.assertEqual(DemographicCleaner.clean_gender("F"), "F")
        self.assertEqual(DemographicCleaner.clean_gender("Male"), "M")
        self.assertEqual(DemographicCleaner.clean_gender("female"), "F")
        self.assertEqual(DemographicCleaner.clean_gender("man"), "M")
        self.assertEqual(DemographicCleaner.clean_gender("woMAn"), "F")

        self.assertEqual(DemographicCleaner.clean_gender(""), None)
        self.assertEqual(DemographicCleaner.clean_gender("f."), None)
        self.assertEqual(DemographicCleaner.clean_gender(" f "), None)
        self.assertEqual(DemographicCleaner.clean_gender("men"), None)
