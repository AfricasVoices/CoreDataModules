from core_data_modules.cleaners import RegexUtils, Codes, DigitCleaner
from core_data_modules.cleaners.somali.demographic_patterns import Patterns


class DemographicCleaner(object):
    @classmethod
    def is_noise(cls, text):
        # Note: Testing is_only_yes_no AND clean_yes_no because
        # is_only_yes_no == True does not imply clean_yes_no does not return Codes.NOT_CODED
        is_demographic = False
        if cls.is_only_yes_no(text) or \
                cls.clean_gender(text) is not Codes.NOT_CODED or \
                cls.clean_yes_no(text) is not Codes.NOT_CODED or \
                cls.clean_urban_rural(text) is not Codes.NOT_CODED or \
                cls.clean_somalia_district(text) is not Codes.NOT_CODED or \
                cls.clean_age(text) is not Codes.NOT_CODED:
            is_demographic = True

        is_noise_by_regex = RegexUtils.has_matches(text, Patterns.noise)

        return is_noise_by_regex and not is_demographic

    @staticmethod
    def is_only_yes_no(text):
        return RegexUtils.has_matches(text, Patterns.only_yes_no)

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
    
    @staticmethod
    def clean_number_words(text):
        """
        Extracts the numbers in the given text that are expressed in words, and converts them to an integer.
        
        The strategy employed searches the given string for each number in somali.Patterns.numbers,
        and returns the sum total of the numbers which matched at least once in the given text.

        >>> DemographicCleaner.clean_number_words("lix iyo lawatan")
        26
        >>> DemographicCleaner.clean_number_words("afar shan lix")
        15

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int
        """
        total = 0
        found_match = False

        for number, pattern in Patterns.numbers.items():
            if RegexUtils.has_matches(text, pattern):
                found_match = True
                total += number

        if found_match:
            return total
        else:
            return Codes.NOT_CODED

    @classmethod
    def clean_age(cls, text):
        """
        Extracts the number from the given text from either digits or words.

        Returns Codes.NotCoded if age <= 10 or age >= 90.

        >>> DemographicCleaner.clean_age("lix iyo lawatan")
        26
        >>> DemographicCleaner.clean_age(" 35.")
        35

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int
        """
        cleaned_digits = DigitCleaner.clean_number_digits(text)
        if cleaned_digits != Codes.NOT_CODED and 10 < int(cleaned_digits) < 90:
            return cleaned_digits

        cleaned_words = cls.clean_number_words(text)
        if cleaned_words != Codes.NOT_CODED and 10 < cleaned_words < 90:
            return cleaned_words

        return Codes.NOT_CODED
