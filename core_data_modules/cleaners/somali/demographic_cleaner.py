from core_data_modules.cleaners import RegexUtils
from core_data_modules.cleaners.somali.demographic_patterns import Patterns


class DemographicCleaner(object):
    @staticmethod
    def clean_gender(text):
        return RegexUtils.clean_with_patterns(text, Patterns.genders)

    @staticmethod
    def clean_yes_no(text):
        return RegexUtils.clean_with_patterns(text, Patterns.yes_no)

    @staticmethod
    def clean_urban_rural(text):
        return RegexUtils.clean_with_patterns(text, Patterns.urban_rural)

    @staticmethod
    def clean_somalia_district(text):
        return RegexUtils.clean_with_patterns(text, Patterns.somalia_districts)
