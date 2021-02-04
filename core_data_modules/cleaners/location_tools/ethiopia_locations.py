from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes import EthiopiaCodes, KenyaCodes


class EthiopiaLocations(object):
    @classmethod
    def is_location_code(cls, text):
        """
        Returns True if the given location argument matches an Ethiopian zone or region code; False otherwise.

        >>> EthiopiaLocations.is_location_code(EthiopiaCodes.ADDIS_ABABA)
        True
        >>> EthiopiaLocations.is_location_code(EthiopiaCodes.REGION_14)
        True
        >>> EthiopiaLocations.is_location_code(EthiopiaCodes.OROMIA)
        True
        >>> EthiopiaLocations.is_location_code(KenyaCodes.NANDI)
        False
        >>> EthiopiaLocations.is_location_code(Codes.MALE)
        False

        :param text: Text to test if contains a location code
        :type text: str
        :return: Whether or not location matches a known kenya location code
        :rtype: bool
        """
        return text in EthiopiaCodes.ZONES or text in EthiopiaCodes.REGIONS

    @staticmethod
    def zone_for_location_code(location_code):
        """
        Returns the Ethiopian zone for the provided Ethiopia location code.

        The provided code may be an Ethiopian zone only.

        >>> EthiopiaLocations.zone_for_location_code(EthiopiaCodes.REGION_14)
        'region 14'
        >>> EthiopiaLocations.zone_for_location_code(EthiopiaCodes.ADDIS_ABABA)
        'NC'

        :param location_code: An Ethiopian zone code
        :type location_code: str
        :return: Ethiopian zone or Codes.NOT_CODED
        :rtype: str
        """
        if location_code in EthiopiaCodes.ZONES:
            return location_code

        return Codes.NOT_CODED

    @classmethod
    def region_for_location_code(cls, location_code):
        """
        Returns the region for the provided Ethiopian location code.

        The provided code may be an Ethiopian zone or region.

        >>> EthiopiaLocations.region_for_location_code(EthiopiaCodes.ADDIS_ABABA)
        'addis ababa'
        >>> EthiopiaLocations.region_for_location_code(EthiopiaCodes.REGION_14)
        'addis ababa'
        >>> EthiopiaLocations.region_for_location_code(EthiopiaCodes.NORTH_SHEWA_OR)
        'oromia'

        :param location_code: An Ethiopian zone or region code
        :type location_code: str
        :return: An Ethiopian region code or Codes.NOT_CODED
        :rtype: str
        """
        zone = cls.zone_for_location_code(location_code)
        if zone != Codes.NOT_CODED:
            location_code = zone

        if location_code in EthiopiaCodes.ZONES:
            return EthiopiaCodes.ZONE_TO_REGION_MAP[location_code]

        if location_code in EthiopiaCodes.REGIONS:
            return location_code

        return Codes.NOT_CODED
