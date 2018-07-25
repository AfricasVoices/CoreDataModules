from core_data_modules.cleaners import RegexUtils
from core_data_modules.cleaners.somali.demographic_patterns import Patterns


class DemographicCleaner(object):
    @staticmethod
    def clean_somalia_district(text):
        return RegexUtils.clean_with_patterns(text, Patterns.somalia_districts)
