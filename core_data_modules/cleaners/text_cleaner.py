# coding=utf-8
import string

import six


class TextCleaner(object):
    @staticmethod
    def to_ascii(text):
        """
        Removes non-ASCII characters from the given input string

        >>> TextCleaner.to_ascii(u"tøåst")
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

    @classmethod
    def clean_text(cls, text):
        """
        Removes non-ASCII characters from the given input string, replaces punctuation characters with spaces, and
        converts to lower case.

        >>> TextCleaner.clean_text(u"aBc,d å ef")
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
