import hashlib
import json
from deprecation import deprecated

import six

from core_data_modules.views.traced_data_keys_view import _TracedDataKeysView


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
    def __init__(self, data, metadata, prev=None):
        self._prev = prev
        self._data = data
        self._sha = self._sha_with_prev(data, "" if prev is None else prev._sha)
        self._metadata = metadata

    @staticmethod
    def _sha_with_prev(data, prev_sha):
        return SHAUtils.sha_dict({"data": data, "prev_sha": prev_sha})

    def __len__(self):
        return sum(1 for _ in six.viewkeys(self))

    def get(self, key, default=None):
        if key in self._data:
            return self._data[key]
        elif self._prev is not None:
            return self._prev.get(key, default)
        else:
            return default

    def __getitem__(self, key):
        return self.get(key)

    def append(self, new_data, new_metadata):
        self._prev = TracedData(self._data, self._metadata, self._prev)
        self._data = new_data
        self._sha = self._sha_with_prev(self._data, self._prev._sha)
        self._metadata = new_metadata

    @deprecated
    def has_key(self, key):
        if self._data.has_key(key):
            return True
        elif self._prev is not None:
            return self._prev.has_key(key)
        else:
            return False

    def __contains__(self, key):
        if key in self._data:
            return True
        elif self._prev is not None:
            return key in self._prev
        else:
            return False

    def items(self):
        if self._prev is None:
            return self._data.items()
        else:
            # TODO: In Python 3 self._prev.items() returns an iterator, which is immediately expanded to build a dict.
            # TODO: Consider a rewrite which does not require performing this expansion.
            prev_items = dict(self._prev.items())
            for (key, value) in six.iteritems(self._data):
                prev_items[key] = value
            return prev_items.items()

    if six.PY2:
        def keys(self):
            if self._prev is None:
                return self._data.keys()
            else:
                prev_items = dict(self._prev.items())
                # noinspection PyCompatibility
                for (key, value) in self._data.iteritems():
                    prev_items[key] = value
                return prev_items.keys()

    if six.PY3:
        def keys(self):
            return _TracedDataKeysView(self)

    def values(self):
        if self._prev is None:
            return self._data.values()
        else:
            prev_items = dict(self._prev.items())
            for (key, value) in six.iteritems(self._data):
                prev_items[key] = value
            return prev_items.values()

    if six.PY2:
        def iteritems(self):
            if self._prev is None:
                return self._data.iteritems()
            else:
                prev_items = dict(self._prev.iteritems())
                for (key, value) in self._data.iteritems():
                    prev_items[key] = value
                return prev_items.iteritems()

        def iterkeys(self):
            return iter(self.viewkeys())

        def viewkeys(self):
            return _TracedDataKeysView(self)

        def itervalues(self):
            if self._prev is None:
                return self._data.itervalues()
            else:
                prev_items = dict(self._prev.iteritems())
                for (key, value) in self._data.iteritems():
                    prev_items[key] = value
                return prev_items.itervalues()

    def __iter__(self):
        return six.iterkeys(self)

    def __copy__(self):
        return TracedData(self._data, self._metadata, self._prev.copy())

    def get_history(self, key):
        history = [] if self._prev is None else self._prev.get_history(key)
        if key in self._data:
            history.append({"sha": self._sha, "value": self._data[key]})
        return history
