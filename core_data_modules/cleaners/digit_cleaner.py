import re

from core_data_modules.cleaners import Codes


class DigitCleaner(object):
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
    def clean_number_digits(cls, text):
        """
        Extracts the digit (and digit-like characters e.g. 'o') from the given text and converts to an integer.

        >>> DigitCleaner.clean_number_digits("I am 2O years old")
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
