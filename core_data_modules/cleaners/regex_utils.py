import re

from core_data_modules.cleaners import Codes


class RegexUtils(object):
    @staticmethod
    def search(pattern, text, flags=0, case=False):
        """
        Searches the given text for regions which match a regex constructed from the given pattern.

        :param pattern: Regex pattern to use
        :type pattern: str
        :param text: Text to run regex over.
        :type text: str
        :param flags: Additional re regex flags. See the documentation for re.compile for details.
        :type flags: int
        :param case: Whether to match case.
        :type case: bool
        :return: regex search results
        :rtype: MatchObject
        """
        # Note: Design based on str.contains in the pandas library. See:
        # https://github.com/pandas-dev/pandas/blob/a00154dcfe5057cb3fd86653172e74b6893e337d/pandas/core/strings.py#L219
        if not case:
            flags |= re.IGNORECASE

        regex = re.compile(pattern, flags=flags)

        return regex.search(text)

    @classmethod
    def has_matches(cls, text, pattern, **kwargs):
        """
        Returns True if the given regex pattern was found in the given text, False otherwise.

        :param text: Text to search for the given pattern.
        :type text: str
        :param pattern: Regex pattern to search the given text for.
        :type pattern: str
        :param kwargs: See the optional arguments in the documentation for Regex.apply.
        :type kwargs: dict of str -> any
        :return: Whether the given pattern was found in the given text.
        :rtype: bool
        """
        return bool(cls.search(pattern, text, **kwargs))

    @staticmethod
    def clean_with_patterns(text, patterns):
        """
        Attempts to clean a string by applying each of the provided regex patterns to the given text.

        The code associated with the first pattern to match is returned.

        :param text: Text to clean.
        :type text: str
        :param patterns: Dictionary of code: pattern pairs.
        :type patterns: dict of str -> str
        :return: Code associated with the first pattern to
        :rtype: str
        """
        for code, pattern in patterns.items():
            if RegexUtils.has_matches(text, pattern):
                # TODO: This follows what Dreams did, but is it really acceptable to just return the first match?
                return code
        return Codes.NotCleaned
