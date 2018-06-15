import re


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

        :param phone: Phone number to normalise
        :type phone: str
        :return: Normalised phone number
        :rtype: str
        """
        return re.sub("[^0-9]", "", phone).lstrip("0")
