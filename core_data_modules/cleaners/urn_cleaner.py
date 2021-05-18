from core_data_modules.cleaners import PhoneCleaner, Codes


class URNCleaner(object):
    @staticmethod
    def clean_operator(urn):
        """
        Returns the operator code for the given urn.

        If the urn is a telephone, returns the operator of the phone line (see `PhoneCleaner.clean_operator`),
        otherwise returns the urn.

        >>> URNCleaner.clean_operator("tel:+25261123123")
        'hormud'
        >>> URNCleaner.clean_operator("tel:+2547123123")
        'kenyan telephone'
        >>> URNCleaner.clean_operator("telegram:123456")
        'telegram'
        >>> URNCleaner.clean_operator("+25261123123")  # (Not a valid urn)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        ValueError

        :param urn: URN number to determine the operator of.
        :type urn: str
        :return: URN operator.
        :rtype: str
        """
        if ":" not in urn:
            raise ValueError
        if urn.startswith("tel:"):
            # Set the operator name from the phone number
            assert urn.startswith("tel:+")
            return PhoneCleaner.clean_operator(urn)
        elif urn.startswith("deleted:"):
            return Codes.DELETED
        else:
            # Set the operator name from the channel type e.g. 'telegram', 'twitter'
            return urn.split(":")[0]
