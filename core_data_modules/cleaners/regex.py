import re


class Regex(object):
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
