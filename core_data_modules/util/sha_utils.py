import hashlib
import json

from core_data_modules.util.text_utils import TextUtils


class SHAUtils(object):
    @staticmethod
    def sha_string(string):
        """
        Hashes the provided string using the SHA-256 algorithm.

        :param string: String to hash.
        :type string: string
        :return: SHA-256 hashed string.
        :rtype: string
        """
        return hashlib.sha256(string.encode("utf-8")).hexdigest()

    @classmethod
    def stringify_dict(cls, d):
        """
        Converts a dict to a JSON string.

        Dictionaries with the same (key, value) pairs are guaranteed to serialize to the same string,
        irrespective of the order in which the keys were added.

        :param d: Dictionary to convert to JSON.
        :type d: dict
        :return: JSON serialization of the given dict.
        :rtype: string
        """
        return json.dumps(d, sort_keys=True)

    @classmethod
    def sha_dict(cls, d):
        """
        Hashes the provided dict using the SHA-256 algorithm.

        :param d: Dictionary to hash.
        :type d: dict
        :return: SHA-256 hashed dict.
        :rtype: string
        """
        return cls.sha_string(cls.stringify_dict(d))

    @staticmethod
    def create_hash_id(text):
        """TODO"""
        h = hashlib.sha1(TextUtils.remove_non_ascii(text).encode("utf-8"))  # TODO: Is SHA1 acceptable? TODO 2: Can we use sha_string?
        n = str(int(h.hexdigest()[:10], 16))[:10]  # TODO:  Refactor into its own method?
        return n
