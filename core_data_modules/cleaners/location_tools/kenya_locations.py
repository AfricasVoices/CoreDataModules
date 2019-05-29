from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes import KenyaCodes


class KenyaLocations(object):
    @classmethod
    def is_location_code(cls, text):
        """
        Returns True if the given location argument matches a kenya constituency or county
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
        return text in KenyaCodes.CONSTITUENCIES or \
               text in KenyaCodes.COUNTIES

    @staticmethod
    def kenya_constituency_for_location_code(location_code):
        """
        Returns the Kenya constituency for the provided Kenya location code.

        The provided code may be a Kenya constituency only.

        >>> KenyaLocations.kenya_constituency_for_location_code(KenyaCodes.NORTH_IMENTI)
        'north imenti'
        >>> KenyaLocations.kenya_constituency_for_location_code(KenyaCodes.NAIROBI)
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
        county = cls.county_for_location_code(location_code)
        if county != Codes.NOT_CODED:
            location_code = county

        if location_code in KenyaCodes.CONSTITUENCIES:
            return KenyaCodes.CONSTITUENCY_TO_COUNTY_MAP[location_code]

        if location_code in KenyaCodes.COUNTIES:
            return location_code

        return Codes.NOT_CODED
