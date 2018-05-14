import hashlib
import json


class SHAUtils(object):
    @staticmethod
    def sha_string(string):
        return hashlib.sha256(string.encode("utf-8")).hexdigest()

    @classmethod
    def stringify_dict(cls, d):
        return json.dumps(d, sort_keys=True)

    @classmethod
    def sha_dict(cls, d):
        return cls.sha_string(cls.stringify_dict(d))
