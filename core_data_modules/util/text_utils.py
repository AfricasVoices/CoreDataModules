import string

import six


# TODO: The functions currently here arguably do cleaning. Move to a TextCleaner class?
class TextUtils(object):
    @staticmethod
    def remove_non_ascii(text):
        """
        Removes non ASCII characters from the given input string

        :param text: String to convert to ASCII.
        :type text: str
        :return: ASCII-encoded string.
        :rtype: str
        """
        return text.encode("ascii", "ignore").decode()

    @classmethod
    def clean_text(cls, text):
        """
        Removes non-ASCII and punctuation characters from the given input string, and converts to lower case.

        :param text: Text to clean
        :type text: str
        :return: Cleaned text
        :rtype: str
        """
        translator = None
        if six.PY2:
            translator = string.maketrans(string.punctuation, " " * len(string.punctuation))
        if six.PY3:
            translator = bytes.maketrans(string.punctuation.encode("ascii"), b" " * len(string.punctuation))

        return text.encode("ascii", "ignore").translate(translator).lower().decode()
