from core_data_modules.cleaners import Codes, DigitCleaner
from core_data_modules.cleaners import RegexUtils

from .demographic_patterns import Patterns


class DemographicCleaner(object):
    @staticmethod
    def clean_gender(text):
        """
        Identifies the gender in the given string.

        >>> DemographicCleaner.clean_gender("KiUMe")
        'man'

        :param text: Text to clean.
        :type text: str
        :return: Codes.Man, Codes.Woman, or None if no gender could be identified.
        :rtype: str
        """
        patterns = {
            Codes.MAN: Patterns.man,
            Codes.WOMAN: Patterns.woman
        }

        return RegexUtils.clean_with_patterns(text, patterns)

    @staticmethod
    def clean_number_units(text):
        """
        Extracts a units-column number expressed in words from the given text, and converts it to an integer.

        >>> DemographicCleaner.clean_number_units("tano")
        5

        :param text: Text to clean.
        :type text: str
        :return: A number from 1-9 inclusive.
        :rtype: int
        """
        patterns = {
            1: Patterns.one,
            2: Patterns.two,
            3: Patterns.three,
            4: Patterns.four,
            5: Patterns.five,
            6: Patterns.six,
            7: Patterns.seven,
            8: Patterns.eight,
            9: Patterns.nine,
        }

        return RegexUtils.clean_with_patterns(text, patterns)

    @staticmethod
    def clean_number_teens(text):
        """
        Extract a "teens" number expressed in words from the given text, and converts it to an integer.

        >>> DemographicCleaner.clean_number_teens("eleven")
        11

        :param text: Text to clean.
        :type text: str
        :return: A number from 11-19 inclusive.
        :rtype: int
        """
        patterns = {
            11: Patterns.eleven,
            12: Patterns.twelve,
            13: Patterns.thirteen,
            14: Patterns.fourteen,
            15: Patterns.fifteen,
            16: Patterns.sixteen,
            17: Patterns.seventeen,
            18: Patterns.eighteen,
            19: Patterns.nineteen
        }

        return RegexUtils.clean_with_patterns(text, patterns)

    @staticmethod
    def clean_number_tens(text):
        """
        Extract a tens-column number expressed in words from the given text, and converts it to an integer.

        >>> DemographicCleaner.clean_number_tens("arobaini")
        40

        :param text: Text to clean.
        :type text: str
        :return: 10, 20, 30, ..., 80, or 90.
        :rtype: int
        """
        patterns = {
            10: Patterns.ten,
            20: Patterns.twenty,
            30: Patterns.thirty,
            40: Patterns.forty,
            50: Patterns.fifty,
            60: Patterns.sixty,
            70: Patterns.seventy,
            80: Patterns.eighty,
            90: Patterns.ninety
        }

        return RegexUtils.clean_with_patterns(text, patterns)

    @classmethod
    def clean_number_words(cls, text):
        """
        Extracts the numbers in the given text that are expressed in words, and converts them to an integer.

        Extracts numbers in the range 1 to 99 inclusive.

        >>> DemographicCleaner.clean_number_words("thirteen")
        13

        >>> DemographicCleaner.clean_number_words("seventy four")
        74

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int
        """
        cleaned_units = cls.clean_number_units(text)
        if cleaned_units == Codes.NOT_CODED:
            cleaned_units = 0

        cleaned_teens = cls.clean_number_teens(text)
        if cleaned_teens == Codes.NOT_CODED:
            cleaned_teens = 0
            
        cleaned_tens = cls.clean_number_tens(text)
        if cleaned_tens == Codes.NOT_CODED:
            cleaned_tens = 0

        cleaned = cleaned_tens + cleaned_teens + cleaned_units

        if cleaned == 0:
            cleaned = Codes.NOT_CODED

        return cleaned
    
    @classmethod
    def clean_number(cls, text):
        """
        Extracts the number from the given text from either digits or words.

        See clean_number_digits and clean_number_words.

        >>> DemographicCleaner.clean_number("40")
        40

        >>> DemographicCleaner.clean_number("seventy-six")
        76

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int
        """
        cleaned_digits = DigitCleaner.clean_number_digits(text)
        if cleaned_digits != Codes.NOT_CODED:
            return cleaned_digits
        else:
            return cls.clean_number_words(text)

    @classmethod
    def clean_age(cls, text):
        """Aliases DemographicCleaner.clean_number"""
        return cls.clean_number(text)

    @staticmethod
    def clean_age_within_range(age, min_age_inclusive=10, max_age_inclusive=99):
        """
        Returns age if age is between the specified min and max acceptable ages, otherwise returns Codes.NOT_CODED

        >>> DemographicCleaner.clean_age_within_range(24)
        24
        >>> DemographicCleaner.clean_age_within_range("24")
        24
        >>> DemographicCleaner.clean_age_within_range(102)
        'NC'
        >>> DemographicCleaner.clean_age_within_range(30, min_age_inclusive=45, max_age_inclusive=55)
        'NC'

        :param age: Age to clamp to the given range.
        :type age: str | int
        :param min_age_inclusive: Minimum age to accept as valid.
        :type min_age_inclusive: int
        :param max_age_inclusive: Maximum age to accept as valid.
        :type max_age_inclusive: int
        :return: age if min_age_inclusive <= age <= max_age_inclusive else Codes.NOT_CODED
        :rtype: int | Codes.NOT_CODED
        """
        if type(age) == str:
            try:
                age = int(age)
            except ValueError:
                return Codes.NOT_CODED

        if age < min_age_inclusive or age > max_age_inclusive:
            return Codes.NOT_CODED

        return age
