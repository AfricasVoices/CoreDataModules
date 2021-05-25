import unittest

from core_data_modules.cleaners.codes import Codes
from core_data_modules.cleaners.english import DemographicCleaner


class TestDemographicCleaner(unittest.TestCase):
    def test_clean_gender(self):
        self.assertEqual(DemographicCleaner.clean_gender("m"), Codes.MAN)
        self.assertEqual(DemographicCleaner.clean_gender("F"), Codes.WOMAN)
        self.assertEqual(DemographicCleaner.clean_gender("Male"), Codes.MAN)
        self.assertEqual(DemographicCleaner.clean_gender("female"), Codes.WOMAN)
        self.assertEqual(DemographicCleaner.clean_gender("man"), Codes.MAN)
        self.assertEqual(DemographicCleaner.clean_gender("woMAn"), Codes.WOMAN)

        self.assertEqual(DemographicCleaner.clean_gender(""), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_gender("f."), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_gender(" f "), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_gender("men"), Codes.NOT_CODED)
