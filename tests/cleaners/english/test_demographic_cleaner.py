import unittest

from core_data_modules.cleaners.codes import Codes
from core_data_modules.cleaners.english import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    def test_clean_gender(self):
        self.assertEqual(DemographicCleaner.clean_gender("m"), Codes.male)
        self.assertEqual(DemographicCleaner.clean_gender("F"), Codes.female)
        self.assertEqual(DemographicCleaner.clean_gender("Male"), Codes.male)
        self.assertEqual(DemographicCleaner.clean_gender("female"), Codes.female)
        self.assertEqual(DemographicCleaner.clean_gender("man"), Codes.male)
        self.assertEqual(DemographicCleaner.clean_gender("woMAn"), Codes.female)

        self.assertEqual(DemographicCleaner.clean_gender(""), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_gender("f."), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_gender(" f "), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_gender("men"), Codes.NOT_CODED)
