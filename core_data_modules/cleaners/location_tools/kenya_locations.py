from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes import KenyaCodes


class KenyaLocations(object):
    @classmethod
    def is_location_code(cls, text):
        """
        Returns True if the given location argument matches a kenya ward, constituency or county
        code; False otherwise.

        >>> KenyaLocations.is_location_code('nairobi')
        True
        >>> KenyaLocations.is_location_code('mombasa')
        True
        >>> KenyaLocations.is_location_code("kisumu")
        True
        >>> KenyaLocations.is_location_code('north imenti')
        True
        >>> KenyaLocations.is_location_code('male')
        False

        :param text: Text to test if contains a location code
        :type text: str
        :return: Whether or not location matches a known kenya location code
        :rtype: bool
        """
        return text in KenyaCodes.WARDS or text in KenyaCodes.CONSTITUENCIES or \
               text in KenyaCodes.COUNTIES

    @staticmethod
    def ward_for_location_code(location_code):
        """
        Returns the Kenya ward for the provided Kenya location code.

        The provided code may be a Kenya constituency only.

        >>> KenyaLocations.ward_for_location_code(KenyaCodes.KIVAA)
        'kivaa'
        >>> KenyaLocations.ward_for_location_code(KenyaCodes.NAIROBI)
        'NC'

        :param location_code: A Kenya ward code
        :type location_code: str
        :return: Kenya ward or Codes.NOT_CODED
        :rtype: str
        """
        if location_code in KenyaCodes.WARDS:
            return location_code

        return Codes.NOT_CODED

    @staticmethod
    def constituency_for_location_code(location_code):
        """
        Returns the Kenya constituency for the provided Kenya location code.

        The provided code may be a Kenya constituency only.

        >>> KenyaLocations.constituency_for_location_code(KenyaCodes.NORTH_IMENTI)
        'north imenti'
        >>> KenyaLocations.constituency_for_location_code(KenyaCodes.NAIROBI)
        'NC'

        :param location_code: A Kenya constituency code
        :type location_code: str
        :return: Kenya constituency or Codes.NOT_CODED
        :rtype: str
        """
        if location_code in KenyaCodes.CONSTITUENCIES:
            return location_code

        return Codes.NOT_CODED

    @classmethod
    def constituency_for_location_code(cls, location_code):
        """
        Returns the constituency for the provided Kenya location code.

        The provided code may be a Kenya ward or a constituency.

        >>> KenyaLocations.constituency_for_location_code(KenyaCodes.KIVAA)
        'masinga'
        >>> KenyaLocations.constituency_for_location_code(KenyaCodes.MASINGA)
        'masinga'

        :param location_code: A Kenya ward or constituency code
        :type location_code: str
        :return: A kenyan constituency code or Codes.NOT_CODED
        :rtype: str
        """
        ward = cls.ward_for_location_code(location_code)
        if ward != Codes.NOT_CODED:
            location_code = ward

        if location_code in KenyaCodes.WARDS:
            return KenyaCodes.WARD_TO_CONSTITUENCY_MAP[location_code]

        if location_code in KenyaCodes.CONSTITUENCIES:
            return location_code

        return Codes.NOT_CODED

    @classmethod
    def county_for_location_code(cls, location_code):
        """
        Returns the county for the provided Kenya location code.

        The provided code may be a Kenya constituency or a county.

        >>> KenyaLocations.county_for_location_code(KenyaCodes.NAIROBI)
        'nairobi'
        >>> KenyaLocations.county_for_location_code(KenyaCodes.NAKURU)
        'nakuru'
        >>> KenyaLocations.county_for_location_code(KenyaCodes.NORTH_IMENTI)
        'meru'

        :param location_code: A Kenya county or constituency code
        :type location_code: str
        :return: A kenyan county code or Codes.NOT_CODED
        :rtype: str
        """
        constituency = cls.constituency_for_location_code(location_code)
        if constituency != Codes.NOT_CODED:
            location_code = constituency

        if location_code in KenyaCodes.CONSTITUENCIES:
            return KenyaCodes.CONSTITUENCY_TO_COUNTY_MAP[location_code]

        if location_code in KenyaCodes.COUNTIES:
            return location_code

        return Codes.NOT_CODED
