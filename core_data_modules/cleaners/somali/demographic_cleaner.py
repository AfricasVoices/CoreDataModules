from core_data_modules.cleaners import RegexUtils, Codes, DigitCleaner
from core_data_modules.cleaners.codes import SomaliaCodes
from core_data_modules.cleaners.somali.demographic_patterns import DemographicPatterns


class DemographicCleaner(object):
    @classmethod
    def is_noise(cls, text, min_length=-1):
        # Note: Testing is_only_yes_no AND clean_yes_no because
        # is_only_yes_no == True does not imply clean_yes_no does not return Codes.NOT_CODED
        is_demographic = False
        if cls.is_only_yes_no(text) or \
                cls.clean_gender(text) is not Codes.NOT_CODED or \
                cls.clean_yes_no(text) is not Codes.NOT_CODED or \
                cls.clean_urban_rural(text) is not Codes.NOT_CODED or \
                cls.clean_somalia_district(text) is not Codes.NOT_CODED or \
                cls.clean_age(text) is not Codes.NOT_CODED:
            is_demographic = True

        is_noise_by_regex = RegexUtils.has_matches(text, DemographicPatterns.noise)
        is_noise_by_compexity = min_length > 0 and len(text) < min_length

        return (is_noise_by_regex or is_noise_by_compexity) and not is_demographic

    @staticmethod
    def is_only_yes_no(text):
        return RegexUtils.has_matches(text, DemographicPatterns.only_yes_no)

    @staticmethod
    def clean_gender(text):
        return RegexUtils.clean_with_patterns(text, DemographicPatterns.genders)

    @staticmethod
    def clean_yes_no(text):
        return RegexUtils.clean_with_patterns(text, DemographicPatterns.yes_no)

    @staticmethod
    def clean_urban_rural(text):
        return RegexUtils.clean_with_patterns(text, DemographicPatterns.urban_rural)

    @staticmethod
    def clean_somalia_district(text):
        return RegexUtils.clean_with_patterns(text, DemographicPatterns.somalia_districts)

    @staticmethod
    def clean_number_words(text):
        """
        Extracts the numbers in the given text that are expressed in words, and converts them to an integer.
        
        The strategy employed searches the given string for each number in somali.Patterns.numbers,
        and returns the sum total of the numbers which matched at least once in the given text.

        >>> DemographicCleaner.clean_number_words("lix iyo lawatan")
        26
        >>> DemographicCleaner.clean_number_words("afar shan lix")
        15

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int
        """
        total = 0
        found_match = False

        for number, pattern in DemographicPatterns.numbers.items():
            if RegexUtils.has_matches(text, pattern):
                found_match = True
                total += number

        if found_match:
            return total
        else:
            return Codes.NOT_CODED

    @classmethod
    def clean_age(cls, text):
        """
        Extracts the number from the given text from either digits or words.

        Returns Codes.NotCoded if age <= 10 or age >= 90.

        >>> DemographicCleaner.clean_age("lix iyo lawatan")
        26
        >>> DemographicCleaner.clean_age(" 35.")
        35

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int
        """
        cleaned_digits = DigitCleaner.clean_number_digits(text)
        if cleaned_digits != Codes.NOT_CODED and 10 < int(cleaned_digits) < 90:
            return cleaned_digits

        cleaned_words = cls.clean_number_words(text)
        if cleaned_words != Codes.NOT_CODED and 10 < cleaned_words < 90:
            return cleaned_words

        return Codes.NOT_CODED

    @staticmethod
    def clean_age_within_range(age, min_age_inclusive=10, max_age_inclusive=99):
        """
        Returns age if age is between the specified min and max acceptable ages, otherwise returns Codes.NOT_CODED

        >>> DemographicCleaner.clean_age_within_range(24)
        24
        >>> DemographicCleaner.clean_age_within_range("24")
        24
        >>> DemographicCleaner.clean_age_within_range(102)
        >>> DemographicCleaner.clean_age_within_range(30, min_age_inclusive=45, max_age_inclusive=55)

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

    @staticmethod
    def get_district(location):
        """
        Returns the district for the provided Somalia location code.

        The provided code may be a Mogadishu sub-district or a district.

        >>> DemographicCleaner.get_district(SomaliaCodes.MOGADISHU)
        'mogadishu'
        >>> DemographicCleaner.get_district(SomaliaCodes.KARAAN)
        'mogadishu'

        :param location: A Somalia district code
        :type location: str
        :return: Somali district or Codes.NOT_CODED
        :rtype: str
        """
        if location in SomaliaCodes.MOGADISHU_SUB_DISTRICTS:
            return SomaliaCodes.MOGADISHU

        if location in SomaliaCodes.DISTRICTS:
            return location

        return Codes.NOT_CODED

    @staticmethod
    def get_region(location):
        """
        Returns the region for the provided Somalia location code.
        
        The provided code may be a Mogadishu sub-district, a district or a region.

        >>> DemographicCleaner.get_region(SomaliaCodes.ADAN_YABAAL)
        'middle shabelle'
        >>> DemographicCleaner.get_region(SomaliaCodes.LOWER_SHABELLE)
        'lower shabelle'

        :param location: A Somalia district or region code
        :type location: str
        :return: Somali region or Codes.NOT_CODED
        :rtype: str
        """
        if location in SomaliaCodes.DISTRICT_TO_REGION_MAP:
            return SomaliaCodes.DISTRICT_TO_REGION_MAP[location]

        if location in SomaliaCodes.REGIONS:
            return location

        return Codes.NOT_CODED

    @classmethod
    def get_state(cls, location):
        """
        Returns the state for the provided Somalia location code.

        The provided code may be a Mogadishu sub-district, a district, a region, or a state.

        >>> DemographicCleaner.get_state(SomaliaCodes.ADAN_YABAAL)
        'hir-shabelle'

        :param location: A Somalia district, region, or state code
        :type location: str
        :return: Somali state or Codes.NOT_CODED
        :rtype: str
        """
        region = cls.get_region(location)
        if region != Codes.NOT_CODED:
            location = region

        if location in SomaliaCodes.REGION_TO_STATE_MAP:
            return SomaliaCodes.REGION_TO_STATE_MAP[location]

        if location in SomaliaCodes.STATES:
            return location

        return Codes.NOT_CODED

    @classmethod
    def get_zone(cls, location):
        """
        Returns the zone for the provided Somalia location code.

        The provided code may be a Mogadishu sub-district, a district, a region, a state, or a zone.

        :param location: A Somalia district, region, state, or zone code
        :type location: str
        :return: Somali zone or Codes.NOT_CODED
        :rtype: str
        """
        state = cls.get_state(location)
        if location != Codes.NOT_CODED:
            location = state

        if location in SomaliaCodes.STATE_TO_ZONE_MAP:
            return SomaliaCodes.STATE_TO_ZONE_MAP[location]

        if location in SomaliaCodes.ZONES:
            return location

        return Codes.NOT_CODED

    @classmethod
    def is_location(cls, location):
        """

        >>> DemographicCleaner.is_location('hodan')
        True
        >>> DemographicCleaner.is_location('mogadishu')
        True
        >>> DemographicCleaner.is_location('scz')
        True
        >>> DemographicCleaner.is_location('male')
        False

        :param location:
        :type location:
        :return: Whether or not location is a
        :rtype: bool
        """
        return location in SomaliaCodes.MOGADISHU_SUB_DISTRICTS or \
            location in SomaliaCodes.DISTRICTS or \
            location in SomaliaCodes.REGIONS or \
            location in SomaliaCodes.STATES or \
            location in SomaliaCodes.ZONES
