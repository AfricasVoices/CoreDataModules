import re

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners import Regex

from .patterns import Patterns
import numpy as np
import sys


class DemographicCleaner(object):
    @staticmethod
    def clean_with_patterns(text, patterns):
        """
        Attempts to clean a string by applying each of the provided regex patterns to the given text.
        
        The code associated with the first pattern to match is returned.

        :param text: Text to clean.
        :type text: str
        :param patterns: Dictionary of code/pattern pairs.
        :type patterns: dict of str -> str
        :return: Code for first matching pattern.
        :rtype: str
        """
        for code, pattern in patterns.items():
            if Regex.has_matches(text, pattern):
                # TODO: This follows what Dreams did, but do we really want to
                return code
        return Codes.NotCleaned

    @classmethod
    def clean_gender(cls, text):
        """
        Identifies the gender in the given string.

        >>> DemographicCleaner.clean_gender("KiUMe")
        'male'

        :param text: Text to clean.
        :type text: str
        :return: Codes.male, Codes.female, or None if no gender could be identified.
        :rtype: str
        """
        patterns = {
            Codes.male: Patterns.male,
            Codes.female: Patterns.female
        }

        return cls.clean_with_patterns(text, patterns)

    @classmethod
    def clean_number_units(cls, text):
        """
        Extracts a units-column number word from the given text, and converts that to an integer.

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

        return cls.clean_with_patterns(text, patterns)

    @classmethod
    def clean_number_teens(cls, text):
        """
        Extract a "teens" number word from the given text.

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

        return cls.clean_with_patterns(text, patterns)

    @classmethod
    def clean_number_tens(cls, text):
        """
        Extract a tens-column number word from the given text, and converts that to an integer.

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

        return cls.clean_with_patterns(text, patterns)

    @staticmethod
    def replace_digit_like_characters(text):
        """
        Replaces letters which look like digits with the digits they look like.

        For example, the characters "o" and "O" are replaced with "0".

        :param text: Text to replace digit-like characters with digits.
        :type text: str
        :return: text with digit-like characters replaced
        :rtype: str
        """
        replacements = {
            "o": "0",
            "i": "1",
            "j": "1",
            "l": "1",
            "z": "2",
            "t": "7"
        }

        for target, replacement in replacements.items():
            text = text.replace(target, replacement)
            text = text.replace(target.upper(), replacement)
        
        return text

    @classmethod
    def clean_number_words(cls, text):
        """
        Extracts the number words in the given text and converts them to an integer.

        Extracts numbers in the range 1 to 99 inclusive.

        For example:
        >>> DemographicCleaner.clean_number_words("thirteen")
        13

        >>> DemographicCleaner.clean_number_words("seventy four")
        74

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int | Codes.NotCleaned
        """
        cleaned_units = cls.clean_number_units(text)
        if cleaned_units == Codes.NotCleaned:
            cleaned_units = 0

        cleaned_teens = cls.clean_number_teens(text)
        if cleaned_teens == Codes.NotCleaned:
            cleaned_teens = 0
            
        cleaned_tens = cls.clean_number_tens(text)
        if cleaned_tens == Codes.NotCleaned:
            cleaned_tens = 0

        cleaned = cleaned_tens + cleaned_teens + cleaned_units

        if cleaned == 0:
            cleaned = Codes.NotCleaned

        return cleaned
    
    @classmethod
    def clean_number_digits(cls, text):
        """
        Extracts the digit (and digit-like characters e.g. 'o') from the given text and converts to an integer.

        >>> DemographicCleaner.clean_number_digits("I am 2O years old")
        '20'

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: str  TODO: Are we sure we don't want int?
        """
        text = cls.replace_digit_like_characters(text)

        matches = re.search(r"(\b\d{2}\b|\b\d\d\b)", text)  # TODO: This regex only extracts 2-digit numbers
        if matches:
            return matches.group(1).strip()
        else:
            return Codes.NotCleaned

    @classmethod
    def clean_number(cls, text):
        """
        Extracts the number from the given text from either digits or words.

        See clean_number_digits and clean_number_words.

        >>> DemographicCleaner.clean_number("40")
        '40'

        >>> DemographicCleaner.clean_number("seventy-six")
        76

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: str | int  # TODO: depends on which function is called eww.
        """
        cleaned_digits = cls.clean_number_digits(text)
        if cleaned_digits != Codes.NotCleaned:
            return cleaned_digits
        else:
            return cls.clean_number_words(text)

    @classmethod
    def clean_age(cls, text):
        """Aliases DemographicCleaner.clean_number"""
        return cls.clean_number(text)
