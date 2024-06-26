import unittest

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes import SomaliaCodes
from core_data_modules.cleaners.somali import DemographicCleaner, DemographicPatterns


class TestDemographicCleaner(unittest.TestCase):
    # Note: These are very much place-holders until we work with AVF's annotation team to produce more complete suites.

    def test_is_noise(self):
        noise = ["kalkaal", "hi", "kal kaal asc", "KALKAL"]
        not_noise = ["my", "ha", "24"]

        for noise_test in noise:
            self.assertTrue(DemographicCleaner.is_noise(noise_test))
        for not_noise_test in not_noise:
            self.assertFalse(DemographicCleaner.is_noise(not_noise_test))

    def test_clean_is_only_yes_no(self):
        self.assertTrue(DemographicCleaner.is_only_yes_no("ha"))
        self.assertTrue(DemographicCleaner.is_only_yes_no("my"))

    def test_clean_genders(self):
        self.assertEqual(DemographicCleaner.clean_gender("woman"), Codes.WOMAN)

    def test_clean_yes_no(self):
        self.assertEqual(DemographicCleaner.clean_yes_no("haa"), Codes.YES)
        # self.assertEqual(DemographicCleaner.clean_yes_no("ha"), Codes.YES)  # TODO: Test fails
        self.assertEqual(DemographicCleaner.clean_yes_no("mayo"), Codes.NO)
        # self.assertEqual(DemographicCleaner.clean_yes_no("my"), Codes.NO)  # TODO: Test fails

    def test_clean_urban_rural(self):
        self.assertEqual(DemographicCleaner.clean_urban_rural("maalo"), Codes.URBAN)
        self.assertEqual(DemographicCleaner.clean_urban_rural("I am a villager."), Codes.RURAL)

    def test_clean_mogadishu_sub_district(self):
        # Check that the patterns defined for the mogadishu sub districts cleaner are all defined in
        # SomaliaCodes.MOGADISHU_SUB_DISTRICTS
        self.assertSetEqual(
            set(DemographicPatterns.mogadishu_sub_districts.keys()) - set(SomaliaCodes.MOGADISHU_SUB_DISTRICTS), set())

        self.assertEqual(DemographicCleaner.clean_mogadishu_sub_district("Hdan is home"), SomaliaCodes.HODAN)

    def test_clean_somalia_district(self):
        # Check that the patterns defined for the somalia districts cleaner are all defined in SomaliaCodes.DISTRICTS
        self.assertSetEqual(set(DemographicPatterns.somalia_districts.keys()) - set(SomaliaCodes.DISTRICTS), set())

        self.assertEqual(DemographicCleaner.clean_somalia_district("I live in Mogadishu"), SomaliaCodes.MOGADISHU)

    def test_clean_number_words(self):
        # TODO: This test fails because fifteen matches both 'ten' and 'fifteen', so cleaner is returning 25.
        # self.assertEqual(DemographicCleaner.clean_number_words("fifteen"), 15)

        self.assertEqual(DemographicCleaner.clean_number_words("lix iyo lawatan"), 26)
        self.assertEqual(DemographicCleaner.clean_number_words("I am thirty"), 30)
        self.assertEqual(DemographicCleaner.clean_number_words("one day I will be twenty"), 1 + 20)

    def test_clean_age(self):
        self.assertEqual(DemographicCleaner.clean_age("lix iyo lawatan"), 26)
        self.assertEqual(DemographicCleaner.clean_age("25"), 25)
        self.assertEqual(DemographicCleaner.clean_age("97"), Codes.NOT_CODED)

    def test_clean_age_range(self):
        self.assertEqual(DemographicCleaner.clean_age_within_range("45"), 45)
        self.assertEqual(DemographicCleaner.clean_age_within_range(17), 17)
        self.assertEqual(DemographicCleaner.clean_age_within_range("4"), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_age_within_range("four"), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_age_within_range("Text not involving a number"), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_age_within_range("10.5"), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_age_within_range("17", min_age_inclusive=20), Codes.NOT_CODED)
        self.assertEqual(DemographicCleaner.clean_age_within_range("17", max_age_inclusive=15), Codes.NOT_CODED)
