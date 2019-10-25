import hashlib
import json


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

    @classmethod
    def sha_file_at_path(cls, file_path, read_block_size=65536):
        """
        Hashes the file at the provided path using the SHA-256 algorithm.
        
        :param file_path: Path to the file to compute the SHA of.
        :type file_path: str
        :param read_block_size: When reading the file, the number of bytes to read at once. 
        :type read_block_size: int
        :return: SHA-256 hash of the file.
        :rtype: str
        """
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(read_block_size)
                if not chunk:
                    break
                sha.update(chunk)
            return sha.hexdigest()
