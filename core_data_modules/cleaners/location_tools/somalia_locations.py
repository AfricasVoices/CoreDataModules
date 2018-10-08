from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes import SomaliaCodes


class SomaliaLocations(object):
    @classmethod
    def is_location_code(cls, text):
        """
        Returns True if the given location argument matches a Mogadishu sub-district code or a Somali
        district, region, state, or zone code; False otherwise.

        >>> SomaliaLocations.is_location_code('hodan')
        True
        >>> SomaliaLocations.is_location_code('mogadishu')
        True
        >>> SomaliaLocations.is_location_code("matabaan")
        True
        >>> SomaliaLocations.is_location_code('scz')
        True
        >>> SomaliaLocations.is_location_code('male')
        False

        :param text: Text to test if contains a location code
        :type text: str
        :return: Whether or not location matches a known Somalia location code
        :rtype: bool
        """
        return text in SomaliaCodes.MOGADISHU_SUB_DISTRICTS or \
               text in SomaliaCodes.DISTRICTS or \
               text in SomaliaCodes.REGIONS or \
               text in SomaliaCodes.STATES or \
               text in SomaliaCodes.ZONES

    @staticmethod
    def district_for_location_code(location_code):
        """
        Returns the district for the provided Somalia location code.

        The provided code may be a Mogadishu sub-district or a district.

        >>> SomaliaLocations.district_for_location_code(SomaliaCodes.MOGADISHU)
        'mogadishu'
        >>> SomaliaLocations.district_for_location_code(SomaliaCodes.KARAAN)
        'mogadishu'
        >>> SomaliaLocations.district_for_location_code(SomaliaCodes.MATABAAN)
        'belet weyne'

        :param location_code: A Somalia district code
        :type location_code: str
        :return: Somali district or Codes.NOT_CODED
        :rtype: str
        """
        if location_code in SomaliaCodes.MOGADISHU_SUB_DISTRICTS:
            return SomaliaCodes.MOGADISHU

        if location_code in SomaliaCodes.CANONICAL_DISTRICT_MAP:
            location_code = SomaliaCodes.CANONICAL_DISTRICT_MAP[location_code]

        if location_code in SomaliaCodes.DISTRICTS:
            return location_code

        return Codes.NOT_CODED

    @classmethod
    def region_for_location_code(cls, location_code):
        """
        Returns the region for the provided Somalia location code.

        The provided code may be a Mogadishu sub-district, a district or a region.

        >>> SomaliaLocations.region_for_location_code(SomaliaCodes.ADAN_YABAAL)
        'middle shabelle'
        >>> SomaliaLocations.region_for_location_code(SomaliaCodes.LOWER_SHABELLE)
        'lower shabelle'

        :param location_code: A Somalia district or region code
        :type location_code: str
        :return: Somali region or Codes.NOT_CODED
        :rtype: str
        """
        district = cls.district_for_location_code(location_code)
        if district != Codes.NOT_CODED:
            location_code = district

        if location_code in SomaliaCodes.DISTRICTS:
            return SomaliaCodes.DISTRICT_TO_REGION_MAP[location_code]

        if location_code in SomaliaCodes.REGIONS:
            return location_code

        return Codes.NOT_CODED

    @classmethod
    def state_for_location_code(cls, location_code):
        """
        Returns the state for the provided Somalia location_code code.

        The provided code may be a Mogadishu sub-district, a district, a region, or a state.

        >>> SomaliaLocations.state_for_location_code(SomaliaCodes.ADAN_YABAAL)
        'hir-shabelle'

        :param location_code: A Somalia district, region, or state code
        :type location_code: str
        :return: Somali state or Codes.NOT_CODED
        :rtype: str
        """
        region = cls.region_for_location_code(location_code)
        if region != Codes.NOT_CODED:
            location_code = region

        if location_code in SomaliaCodes.REGIONS:
            return SomaliaCodes.REGION_TO_STATE_MAP[location_code]

        if location_code in SomaliaCodes.STATES:
            return location_code

        return Codes.NOT_CODED

    @classmethod
    def zone_for_location_code(cls, location_code):
        """
        Returns the zone for the provided Somalia location code.

        The provided code may be a Mogadishu sub-district, a district, a region, a state, or a zone.

        >>> SomaliaLocations.zone_for_location_code(SomaliaCodes.MATABAAN)
        'scz'

        :param location_code: A Somalia district, region, state, or zone code
        :type location_code: str
        :return: Somali zone or Codes.NOT_CODED
        :rtype: str
        """
        state = cls.state_for_location_code(location_code)
        if location_code != Codes.NOT_CODED:
            location_code = state

        if location_code in SomaliaCodes.STATES:
            return SomaliaCodes.STATE_TO_ZONE_MAP[location_code]

        if location_code in SomaliaCodes.ZONES:
            return location_code

        return Codes.NOT_CODED

    @classmethod
    def zone_for_operator_code(cls, operator_code):
        """
        Returns the zone for the provided Somalia operator code.

        >>> SomaliaLocations.zone_for_operator_code(SomaliaCodes.TELESOM)
        'nwz'

        :param operator_code: Somalia operator code to return the zone for
        :type operator_code: str
        :return: Somali zone or Codes.NOT_CODED
        :rtype: str
        """
        return SomaliaCodes.OPERATOR_TO_ZONE_MAP.get(operator_code, Codes.NOT_CODED)
