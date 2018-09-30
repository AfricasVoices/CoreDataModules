import re

from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes.somalia_codes import SomaliaCodes


class PhoneCleaner(object):
    @staticmethod
    def normalise_phone(phone):
        """
        Normalises a phone number string by removing all non numeric characters and dropping any leading 0s.

        For example:
        >>> PhoneCleaner.normalise_phone("+254123123")
        '254123123'
        >>> PhoneCleaner.normalise_phone("  254-(123) 123")
        '254123123'
        >>> PhoneCleaner.normalise_phone("0254123123")
        '254123123'
        >>> PhoneCleaner.normalise_phone("0123123")
        '123123'
        >>> PhoneCleaner.normalise_phone("0-0 0123123")
        '123123'
        >>> PhoneCleaner.normalise_phone("tel:+254123123")
        '254123123'
        >>> PhoneCleaner.normalise_phone("tel:0123123")
        '123123'

        :param phone: Phone number to normalise
        :type phone: str
        :return: Normalised phone number
        :rtype: str
        """
        return re.sub("[^0-9]", "", phone).lstrip("0")

    @classmethod
    def clean_operator(cls, phone_number):
        """
        Returns the operator code for the given (Somali) phone number.

        >>> PhoneCleaner.clean_operator("+252 612 000")
        'hormud'
        >>> PhoneCleaner.clean_operator("252 612 000")
        'hormud'
        >>> PhoneCleaner.clean_operator("  a 252 624 000")
        'somtel'
        >>> PhoneCleaner.clean_operator("not a phone number")
        'NC'

        :param phone_number: Phone number to determine the operator of.
                             This does not need to be normalised, but must start with the country code.
        :type phone_number: str
        :return: Code of telephone operator or Codes.NOT_CODED
        :rtype: str
        """
        somalia_operator_prefixes = {
            "25261": SomaliaCodes.HORMUD,
            "25262": SomaliaCodes.SOMTEL,
            "25263": SomaliaCodes.TELESOM,
            "25264": SomaliaCodes.HORMUD,
            "25265": SomaliaCodes.SOMTEL,
            "25266": SomaliaCodes.SOMTEL,
            "25267": SomaliaCodes.NATIONLINK,
            "25268": SomaliaCodes.NATIONLINK,
            "25269": SomaliaCodes.NATIONLINK,
            "25290": SomaliaCodes.GOLIS
        }

        normalised_phone_number = cls.normalise_phone(phone_number)
        normalised_prefix = normalised_phone_number[:5]

        return somalia_operator_prefixes.get(normalised_prefix, Codes.NOT_CODED)
