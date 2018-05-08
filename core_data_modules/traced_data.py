import hashlib
import json
import time
from deprecation import deprecated

import six


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


class Metadata(object):
    def __init__(self, user, program, timestamp):
        self.user = user
        self.program = program
        self.timestamp = timestamp


class TracedData(object):
    def __init__(self, data, user, program, prev=None):
        self.__prev = prev
        self.__data = data
        self.__sha = self.__sha_with_prev(data, "" if prev is None else prev.__sha)
        self.__metadata = Metadata(user, program, time.time())

    @staticmethod
    def __sha_with_prev(data, prev_sha):
        return SHAUtils.sha_dict({"data": data, "prev_sha": prev_sha})

    def __len__(self):
        if self.__prev is None:
            return len(self.__data)
        else:
            return len(self.__data) + len(self.__prev)

    def get(self, key, default=None):
        if key in self.__data:
            return self.__data[key]
        elif self.__prev is not None:
            return self.__prev.get(key, default)
        else:
            return default

    def __getitem__(self, key):
        return self.get(key)

    def append(self, new_data, user, program):
        self.__prev = TracedData(self.__data, self.__metadata.user, self.__metadata.program, self.__prev)
        self.__data = new_data
        self.__sha = self.__sha_with_prev(self.__data, self.__prev.__sha)
        self.__metadata = Metadata(user, program, time.time())

    @deprecated
    def has_key(self, key):
        if self.__data.has_key(key):
            return True
        elif self.__prev is not None:
            return self.__prev.has_key(key)
        else:
            return False

    def __contains__(self, key):
        if key in self.__data:
            return True
        elif self.__prev is not None:
            return key in self.__prev
        else:
            return False

    def items(self):
        if self.__prev is None:
            return self.__data.items()
        else:
            # TODO: In Python 3 self.__prev.items() returns an iterator, which is immediately expanded to build a dict.
            # TODO: Consider a rewrite which does not require performing this expansion.
            prev_items = dict(self.__prev.items())
            for (key, value) in six.iteritems(self.__data):
                prev_items[key] = value
            return prev_items.items()

    def keys(self):
        if self.__prev is None:
            return self.__data.keys()
        else:
            prev_items = dict(self.__prev.items())
            for (key, value) in six.iteritems(self.__data):
                prev_items[key] = value
            return prev_items.keys()

    def values(self):
        if self.__prev is None:
            return self.__data.values()
        else:
            prev_items = dict(self.__prev.items())
            for (key, value) in six.iteritems(self.__data):
                prev_items[key] = value
            return prev_items.values()

    if six.PY2:
        def iteritems(self):
            if self.__prev is None:
                return self.__data.iteritems()
            else:
                prev_items = dict(self.__prev.iteritems())
                for (key, value) in self.__data.iteritems():
                    prev_items[key] = value
                return prev_items.iteritems()

        def iterkeys(self):
            if self.__prev is None:
                return self.__data.iterkeys()
            else:
                prev_items = dict(self.__prev.iteritems())
                for (key, value) in self.__data.iteritems():
                    prev_items[key] = value
                return prev_items.iterkeys()

        def itervalues(self):
            if self.__prev is None:
                return self.__data.itervalues()
            else:
                prev_items = dict(self.__prev.iteritems())
                for (key, value) in self.__data.iteritems():
                    prev_items[key] = value
                return prev_items.itervalues()

    def __iter__(self):
        return six.iterkeys(self)
