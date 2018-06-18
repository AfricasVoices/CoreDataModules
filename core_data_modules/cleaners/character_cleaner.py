# coding=utf-8
import string

import six


class CharacterCleaner(object):
    """
    Provides language-agnostic cleaning functions which operate on individual characters.

    These should generally be useful as pre-processing steps before further cleaning functions are applied.
    """

    @staticmethod
    def to_ascii(text):
        """
        Removes non-ASCII characters from the given input string.

        >>> CharacterCleaner.to_ascii(u"tøåst")
        'tst'

        :param text: String to convert to ASCII.
        :type text: str | unicode
        :return: ASCII-encoded string.
        :rtype: str
        """
        if six.PY2:
            return text.encode("ascii", "ignore")
        if six.PY3:
            return text.encode("ascii", "ignore").decode()

    @staticmethod
    def fold_lines(text):
        """
        Converts a multi-line string to a single line string by replacing new lines with spaces.

        >>> CharacterCleaner.fold_lines("a\\nb")
        'a b'

        :param text: String to fold
        :type text: str | unicode
        :return: Folded string
        :rtype: str | unicode
        """
        return text.replace("\n", " ")

    @classmethod
    def clean_text(cls, text):
        """
        Removes non-ASCII characters from the given input string, replaces punctuation characters with spaces, and
        converts to lower case.

        >>> CharacterCleaner.clean_text(u"aBc,d å ef")
        'abc d  ef'

        :param text: Text to clean
        :type text: str | unicode
        :return: Cleaned text
        :rtype: str
        """
        translator = None
        if six.PY2:
            translator = string.maketrans(string.punctuation, " " * len(string.punctuation))
        if six.PY3:
            translator = bytes.maketrans(string.punctuation.encode("ascii"), b" " * len(string.punctuation))

        return cls.to_ascii(text).translate(translator).lower()
