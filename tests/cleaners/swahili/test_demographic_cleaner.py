import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal

from core_data_modules.cleaners.swahili.demographic_cleaner import Cleaners


class TestDemographicCleaner(unittest.TestCase):
    def test_clean_gender(self):
        gender_col = "Gender"
        genders = {gender_col: ["Kiume", "NaN"]}
        df = pd.DataFrame(data=genders)

        cleaned_genders = {gender_col: ["Kiume", "NaN"], gender_col + "_clean": ["male", None]}
        df_expected = pd.DataFrame(data=cleaned_genders)

        Cleaners().clean_gender(df, gender_col)

        assert_frame_equal(df, df_expected)
